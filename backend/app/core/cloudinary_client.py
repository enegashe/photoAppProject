import cloudinary
from cloudinary import CloudinaryResource
from cloudinary.uploader import upload
from app.core.config import CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, CLOUDINARY_CLOUD_NAME
import cloudinary.api, cloudinary.uploader


# Initialize Cloudinary client
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)
def upload_image(file) -> CloudinaryResource:
    """
    Upload an image to Cloudinary and return the resource.

    :param file: The file-like object containing the image data to upload.
    :return: CloudinaryResource object containing details of the uploaded image.
    """
    response = upload(file)
    return response

def delete_image(public_id: str) -> None:
    """
    Delete an image from Cloudinary using its public ID.

    :param public_id: The public ID of the image to delete.
    """
    cloudinary.uploader.destroy(public_id)
def get_image_url(public_id: str) -> str:
    """
    Get the URL of an image stored in Cloudinary.

    :param public_id: The public ID of the image.
    :return: URL of the image.
    """
    return cloudinary.CloudinaryImage(public_id).build_url()

def get_image_metadata(public_id: str) -> dict:
    """
    Get metadata of an image stored in Cloudinary.

    :param public_id: The public ID of the image.
    :return: Dictionary containing metadata of the image.
    """
    return cloudinary.api.resource(public_id)
def list_images() -> list:
    """
    List all images stored in Cloudinary.
    :return: List of dictionaries containing details of each image.
    """
    response = cloudinary.api.resources(type="upload", resource_type="image")
    return response.get("resources", [])
