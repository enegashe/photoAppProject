from app.schemas.image import ImageCreate, ImageOut
from app.models.image import Image
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

def create_image(db: Session, image_in: ImageCreate) -> Image:
    """Create a new image record in the database."""
    image = Image(
        user_id=image_in.user_id,
        url=image_in.url,
        public_id=image_in.public_id,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image
def get_image(db: Session, image_id: int) -> Optional[Image]:
    """Fetch an image by its ID."""
    return db.query(Image).filter(Image.id == image_id).first()

def get_images_by_user(db: Session, user_id: int, skip = 0, limit = 20) -> List[ImageOut]:
    """Fetch all images uploaded by a specific user."""
    return db.query(Image).filter(Image.user_id == user_id).offset(skip).limit(limit).all()

def delete_image(db: Session, image_id: int) -> Optional[Image]:
    """Delete an image by its ID."""
    image = db.query(Image).filter(Image.id == image_id).first()
    if image:
        db.delete(image)
        db.commit()
        return image
    return None