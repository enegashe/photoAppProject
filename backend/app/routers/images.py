from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app import models
from app.crud import image as image_crud
from app.core import cloudinary_client
from app.dependencies import get_current_user
from app.schemas import image as image_schemas
from app.db import get_db
import io
from fastapi_limiter.depends import RateLimiter
router = APIRouter()

"""
Below is the code for image upload. The path is POST /images/upload.
This endpoint allows users to upload images to the application, which are then stored in Cloudinary and the database.
Field Descriptions:
- `image_in`: A multipart form data UploadFile containing the image file and metadata. The data is first checked for authentication, ensuring it is not larger than 10MB or smaller than 1KB.
The format should be a valid image type (e.g., JPEG, PNG). 
- `db`: A database session dependency that provides access to the database.
Returns:
- A JSON response containing the image details if the upload is successful.
"""
@router.post("/upload", response_model=image_schemas.ImageOut, dependencies=[Depends(RateLimiter(times=5, seconds=60))] )
def upload_image(
    image_in: UploadFile,
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(get_current_user),
):
    contents = image_in.file.read()
    size = len(contents)
    if size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image file is too large. Maximum size is 10MB.")
    if size < 1024:
        raise HTTPException(status_code=400, detail="Image file is too small. Minimum size is 1KB.")

    # Validate content type
    if image_in.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(status_code=400, detail="Invalid image file type. Only JPEG, PNG, and GIF are allowed.")

    # Upload to Cloudinary
    upload_response = cloudinary_client.upload_image(io.BytesIO(contents))
    if not upload_response:
        raise HTTPException(status_code=500, detail="Failed to upload image to Cloudinary")

    # Save to DB
    img_in = image_schemas.ImageCreate(
        user_id=current_user.id,
        url=upload_response["url"],
        public_id=upload_response["public_id"],
    )
    image = image_crud.create_image(db=db, image_in=img_in)
    if not image:
        raise HTTPException(status_code=500, detail="Failed to save image details to the database")

    return image



"""
Below is the code for image retrieval. The path is GET /images/{image_id}. It should verify the image belongs 
to the current user (via get_current_user) and return { "id": ..., "url": ..., "uploaded_at": ... }.
Field Descriptions:
- `image_id`: The ID of the image to retrieve.
- `db`: A database session dependency that provides access to the database.
Returns:
- A JSON response containing the image details if the retrieval is successful.
"""
@router.get("/{image_id}", response_model=image_schemas.ImageOut, dependencies=[Depends(RateLimiter(times=5, seconds=60))] )
def get_image(image_id: int, db: Session = Depends(get_db), current_user: models.user.User = Depends(get_current_user)):
    # Check if the image exists
    image = image_crud.get_image(db, image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    # Check if the image belongs to the current user
    if image.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this image")
 
    return image # Return the image details

"""
Below is the code for image deletion. The path is DELETE /images/{image_id}. It should verify the image belongs
to the current user (via get_current_user) and delete the image from both Cloudinary and the database.
Field Descriptions:
- `image_id`: The ID of the image to delete.
- `db`: A database session dependency that provides access to the database.
Returns:
- A JSON response containing the deleted image details if the deletion is successful.
"""
@router.delete("/{image_id}", response_model=image_schemas.ImageOut, dependencies=[Depends(RateLimiter(times=5, seconds=60))] )
def delete_image(image_id: int, db: Session = Depends(get_db), current_user: models.user.User = Depends(get_current_user)):
    # Check if the image exists
    image = image_crud.get_image(db, image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    # Check if the image belongs to the current user
    if image.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this image")
    
    # Delete the image from Cloudinary
    cloudinary_client.delete_image(image.public_id)
    
    # Delete the image from the database
    deleted_image = image_crud.delete_image(db, image_id)
    if not deleted_image:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete image from database")
    
    return deleted_image

"""Below is the code for listing images. The path is GET /images. It should return a list of images uploaded by the current user.
Field Descriptions:
- `skip`: The number of images to skip (for pagination).
- `limit`: The maximum number of images to return (for pagination).
- `db`: A database session dependency that provides access to the database.
Returns:
- A JSON response containing a list of images uploaded by the current user.
"""
@router.get("/", response_model=list[image_schemas.ImageOut], dependencies=[Depends(RateLimiter(times=5, seconds=60))] )
def list_images(skip: int = 0, limit: int = 20, db: Session = Depends(get_db), current_user: models.user.User = Depends(get_current_user)):
    # Fetch images uploaded by the current user
    images = image_crud.get_images_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    
    return images

