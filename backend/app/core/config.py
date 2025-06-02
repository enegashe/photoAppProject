import os

# Load environment variables from a .env file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
SECRET_KEY = os.getenv("SECRET_KEY", "defaultsecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "your_cloudinary_api_key")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "your_cloudinary_api_secret")
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "your_cloudinary_cloud_name")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")