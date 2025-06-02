from sqlalchemy import Column, Integer, String, Boolean
from app.db import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Foreign key to User table
    url = Column(String, nullable=False)  # URL of the image
    public_id = Column(String, unique=True, nullable=False)  # Unique identifier for the image in Cloudinary
    processed = Column(Boolean, default=False)  # Whether the image has been processed
    created_at = Column(String, nullable=False)  # Timestamp of when the image was uploaded
    updated_at = Column(String, nullable=True)  # Timestamp of the last update to the image