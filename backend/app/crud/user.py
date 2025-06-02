from app.schemas.auth import UserCreate
from app.models.user import User
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import EmailStr
from passlib.context import CryptContext

# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_email: EmailStr) -> Optional[User]:
    """Fetch a user by their email."""
    return db.query(User).filter(User.email == user_email).first()
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Fetch a user by their ID."""
    return db.query(User).filter(User.id == user_id).first()
def create_user(db: Session, user: UserCreate) -> User:
    encryptedPassword = pwd_context.hash(user.password) # Encrypt the password using pbkdf2_sha256
    user = User(email=user.email, hashed_password=encryptedPassword) # Create a new User instance with the provided email and encrypted password
    db.add(user) # Add the user instance to the session (in memory)
    db.commit() # Commit the session to save the user to the database
    db.refresh(user) # Refresh the instance to get the updated data from the database (saving it to memory)
    return user

def authenticate_user(db: Session, user_email: EmailStr, password: str) -> Optional[User]:
    user = get_user(db, user_email) # Fetch the user by email
    # If user does not exist or password does not match, return None
    if not user:
        return None
    if not pwd_context.verify(password, user.hashed_password): # Verify the provided password against the stored hashed password
        return None # If the password does not match, return None
    return user # If the user exists and the password matches, return the user instance