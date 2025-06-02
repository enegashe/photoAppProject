from pydantic import BaseModel, EmailStr
from typing import Literal

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: Literal["bearer"]

class TokenPair(Token):
    refresh_token: str

class RefreshTokenIn(BaseModel):
    refresh_token: str