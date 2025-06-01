from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud
from app.dependencies import get_db
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import datetime, timedelta
from jose import jwt

router = APIRouter()
"""
Below is the code for user signup.

Field Descriptions:
- `user_in`: An instance of `schemas.UserCreate` containing the user's email and password.
- `db`: A database session dependency that provides access to the database.

Returns:
- A JSON response containing the access token and token type if the signup is successful.
"""
@router.post("/signup", response_model=schemas.Token)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if the user already exists
    existing = crud.user.get_user_by_email(db, user_in.email) # Check if the user already exists
    if existing:
        raise HTTPException(400, "Email already registered") # If the user already exists, raise an error
    user = crud.user.create_user(db, user_in) # Create a new user with the provided details


    # create JWT
    to_encode = {"sub": str(user.email), "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)} # Encode the email and expiration time into the token
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # Encode the token using the secret key and algorithm
    return {"access_token": token, "token_type": "bearer"} # Return the token and token type as a response

"""
Below is the code for user login.

Field Descriptions:
- `user_in`: An instance of `schemas.UserLogin` containing the user's email and password.
- `db`: A database session dependency that provides access to the database.

Returns:
- A JSON response containing the access token and token type if the login is successful.
"""
@router.post("/login", response_model=schemas.Token)
def login(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    # Authenticate the user
    user = crud.user.authenticate_user(db, user_in.email, user_in.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    
    # create JWT
    to_encode = {"sub": str(user.email), "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}