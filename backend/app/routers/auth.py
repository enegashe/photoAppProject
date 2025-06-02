from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import schemas, crud
from app.dependencies import get_current_user, get_db
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from datetime import datetime, timedelta
from jose import jwt
from app.models.user import RefreshToken
import uuid
from fastapi_limiter.depends import RateLimiter
from jose import JWTError

router = APIRouter()
def create_access_token(subject: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": subject, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(subject: str):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    jti = str(uuid.uuid4())
    to_encode = {"sub": subject, "exp": expire, "jti": jti, "type": "refresh"}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token, jti, expire
"""
Below is the code for user signup.

Field Descriptions:
- `user_in`: An instance of `schemas.UserCreate` containing the user's email and password.
- `db`: A database session dependency that provides access to the database.

Returns:
- A JSON response containing the access token and token type if the signup is successful.
"""
@router.post("/signup", response_model=schemas.auth.TokenPair, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def signup(user_in: schemas.auth.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.user.get_user(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = crud.user.create_user(db, user_in)
    subject = str(user.id)

    # 1) Create access token
    access_token = create_access_token(subject)

    # 2) Create refresh token + store its jti in DB
    refresh_token, jti, expires_at = create_refresh_token(subject)
    db.add(RefreshToken(jti=jti, user_id=user.id, expires_at=expires_at))
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

"""
Below is the code for user login.

Field Descriptions:
- `user_in`: An instance of `schemas.UserLogin` containing the user's email and password.
- `db`: A database session dependency that provides access to the database.

Returns:
- A JSON response containing the access token and token type if the login is successful.
"""
@router.post("/login", response_model=schemas.auth.TokenPair, dependencies=[Depends(RateLimiter(times=5, seconds=60))] )
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.user.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = str(user.id)
    access_token = create_access_token(subject)
    refresh_token, jti, expires_at = create_refresh_token(subject)

    # Save refresh token in DB
    db.add(RefreshToken(jti=jti, user_id=user.id, expires_at=expires_at))
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=schemas.auth.Token, dependencies=[Depends(RateLimiter(times=5, seconds=60))] )
def refresh_token(
    refresh: schemas.auth.RefreshTokenIn,  # simple schema with one field
    db: Session = Depends(get_db)
):
    # 1) Decode & verify JWT (signature + expiry)
    try:
        payload = jwt.decode(refresh.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # 2) Ensure it's actually a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")

    user_id = payload.get("sub")
    jti = payload.get("jti")
    if user_id is None or jti is None:
        raise HTTPException(status_code=401, detail="Malformed token")

    # 3) Look up the jti in the DB, check it's not revoked or expired
    db_token = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
    if not db_token or db_token.revoked or db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token invalid or expired")

    # 4) Issue a new access token
    new_access = create_access_token(subject=user_id)
    db_token.revoked = True
    new_refresh, new_jti, new_exp = create_refresh_token(user_id)
    db.add(RefreshToken(jti=new_jti, user_id=user_id, expires_at=new_exp))
    db.commit()
    return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}
"""
Below is the code for user logout.
Field Descriptions:
- `refresh`: An instance of `schemas.auth.RefreshTokenIn` containing the refresh token.
- `db`: A database session dependency that provides access to the database.
Returns:
- A JSON response indicating the refresh token has been revoked and the user has been logged out.
"""
@router.post("/logout", dependencies=[Depends(RateLimiter(times=5, seconds=60))] )
def logout(
    refresh: schemas.auth.RefreshTokenIn,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)   # ensure user is logged in
):
    # Decode to get jti
    try:
        payload = jwt.decode(refresh.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    jti = payload.get("jti")
    if jti is None:
        raise HTTPException(status_code=400, detail="Token missing jti")

    # Mark it revoked in DB
    db_token = db.query(RefreshToken).filter(RefreshToken.jti == jti, RefreshToken.user_id == current_user.id).first()
    if db_token:
        db_token.revoked = True
        db.commit()

    return {"message": "Refresh token revoked, user logged out"}