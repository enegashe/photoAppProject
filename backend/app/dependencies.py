from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db
from jose import jwt
from app.models.user import User  # Import the User model
from app.crud.user import get_user  # Import the get_user function to fetch user details

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") # This sets the token URL for OAuth2 password flow

"""
Dependency to get the current user based on the provided token.
This function will be used in routes that require authentication.

Field Descriptions:
- `token`: The OAuth2 token provided by the user, extracted using the `oauth2_scheme`.
- `db`: A database session dependency that provides access to the database.

Returns:
- The user object if the token is valid and the user exists, otherwise returns None.
"""
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    decoded = jwt.decode(token, options={"verify_signature": False})  # Decode the token without verifying the signature
    decoded_user_id = decoded["sub"]  # Extract the user ID from the token
    if decoded_user_id is not None:
        user = get_user(db, decoded_user_id)
        if user:
            return user  # Return the user if found
    return None