from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, images, edits, history
from fastapi_limiter import FastAPILimiter
from app.core.config import REDIS_URL
import redis.asyncio as aioredis

# Import database initialization / event handlers
from app import db, core
from dotenv import load_dotenv
load_dotenv()
app = FastAPI(
    title="ML Photo Editor API",
    version="0.1.0",
    description="Backend for ML-powered mobile photo editor"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in prod, lock this down
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Each router file defines an APIRouter() and some path operations
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(images.router, prefix="/images", tags=["images"])
#app.include_router(edits.router, prefix="/edits", tags=["edits"])
#app.include_router(history.router, prefix="/history", tags=["history"])

# Startup event: create tables or connect to any services
@app.on_event("startup")
async def startup_event():
    # Initialize the database
    db.init_db()
    redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis)
    pass


# Root endpoint for health check
@app.get("/")
def read_root():
    return {"message": "ML Photo Editor API is running."}
