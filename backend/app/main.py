from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base
from app.api import auth, books, semesters, users, reads, comments, statistics, shareable_links
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Note: We use Alembic for migrations, so we don't call create_all here
# Base.metadata.create_all(bind=engine)  # Disabled - use Alembic migrations instead

app = FastAPI(
    title=settings.APP_NAME,
    description="CookBomPy - Book Management Platform",
    version="1.0.0",
)

# CORS middleware for Vue dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(books.router, prefix="/api")
app.include_router(semesters.router, prefix="/api")
app.include_router(statistics.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(reads.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(shareable_links.router, prefix="/api")

# Serve static files for media (covers, etc.)
media_path = os.path.join(os.path.dirname(__file__), "..", "media")
os.makedirs(media_path, exist_ok=True)
app.mount("/media", StaticFiles(directory=media_path), name="media")


@app.get("/")
def root():
    return {"message": "CookBomPy API", "version": "1.0.0"}


@app.get("/api/health")
def health():
    """Health check endpoint"""
    return {"status": "ok"}

