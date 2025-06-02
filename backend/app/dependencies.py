from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import SECRET_KEY, ALGORITHM
from app.crud.user import get_user_by_id
from app.models.user import RefreshToken
from app.db import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
""" Below is the code for getting the current user from the access token.
This function decodes the JWT token, checks its validity, and retrieves the user from the database.
Field Descriptions:
- `token`: The JWT access token provided by the user.
- `db`: A database session dependency that provides access to the database.
Returns:
- The user object if the token is valid and the user exists in the database.
"""
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise credentials_exception

    # 1) Check token type
    if payload.get("type") != "access":
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # 2) Look up the user from DB
    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user
