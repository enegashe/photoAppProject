from pydantic import BaseModel

class ImageCreate(BaseModel):
    user_id: int
    url: str
    public_id: str

    class Config:
        orm_mode = True  # Allows Pydantic to work with SQLAlchemy models

class ImageOut(BaseModel):
    id: int
    user_id: int
    url: str
    public_id: str
    processed: bool = False
    created_at: str
    updated_at: str | None = None

    class Config:
        orm_mode = True  # Allows Pydantic to work with SQLAlchemy models