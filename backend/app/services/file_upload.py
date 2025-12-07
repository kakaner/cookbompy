import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
import logging

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class FileUploadService:
    """Service for handling file uploads (cover images, read vibe photos)"""
    
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    def __init__(self, base_media_path: str = "media"):
        self.base_media_path = Path(base_media_path)
        self.base_media_path.mkdir(parents=True, exist_ok=True)
    
    async def upload_cover_image(self, file: UploadFile, user_id: int, book_id: int) -> str:
        """
        Upload cover image for a book
        Returns: URL path to the uploaded file
        """
        # Validate file
        self._validate_file(file)
        
        # Generate file path
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.ALLOWED_EXTENSIONS:
            file_extension = ".jpg"  # Default to jpg
        
        file_path = self.base_media_path / "covers" / str(user_id) / f"{book_id}{file_extension}"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file
        try:
            contents = await file.read()
            
            # Validate file size
            if len(contents) > self.MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(contents)
            
            # Optionally create thumbnail (for future use)
            # self._create_thumbnail(file_path)
            
            # Return relative URL path
            return f"/media/covers/{user_id}/{book_id}{file_extension}"
            
        except Exception as e:
            logger.error(f"Error uploading cover image: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload cover image")
    
    async def upload_read_vibe_photo(self, file: UploadFile, user_id: int, read_id: int) -> str:
        """
        Upload read vibe photo for a specific read
        Returns: URL path to the uploaded file
        """
        # Validate file
        self._validate_file(file)
        
        # Generate file path
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.ALLOWED_EXTENSIONS:
            file_extension = ".jpg"
        
        # Use timestamp to make unique filename
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = self.base_media_path / "read_vibes" / str(user_id) / f"{read_id}_{timestamp}{file_extension}"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file
        try:
            contents = await file.read()
            
            # Validate file size
            if len(contents) > self.MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(contents)
            
            # Return relative URL path
            return f"/media/read_vibes/{user_id}/{read_id}_{timestamp}{file_extension}"
            
        except Exception as e:
            logger.error(f"Error uploading read vibe photo: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload read vibe photo")
    
    async def upload_profile_photo(self, file: UploadFile, user_id: int) -> str:
        """
        Upload profile photo for a user
        Returns: URL path to the uploaded file
        """
        # Validate file
        self._validate_file(file)
        
        # Generate file path
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.ALLOWED_EXTENSIONS:
            file_extension = ".jpg"
        
        file_path = self.base_media_path / "profiles" / f"{user_id}{file_extension}"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file
        try:
            contents = await file.read()
            
            # Validate file size
            if len(contents) > self.MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(contents)
            
            # Create thumbnail for profile (smaller size)
            self._create_thumbnail(file_path, max_size=(200, 200))
            
            # Return relative URL path
            return f"/media/profiles/{user_id}{file_extension}"
            
        except Exception as e:
            logger.error(f"Error uploading profile photo: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload profile photo")
    
    def _validate_file(self, file: UploadFile):
        """Validate uploaded file"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        # Check content type
        content_type = file.content_type
        if content_type and not any(
            content_type.startswith(f"image/{ext.replace('.', '')}")
            for ext in self.ALLOWED_EXTENSIONS
        ):
            raise HTTPException(status_code=400, detail="File must be an image")
    
    def _create_thumbnail(self, file_path: Path, max_size: tuple = (300, 450)):
        """Create thumbnail for image (optional, for future use)"""
        if not PIL_AVAILABLE:
            logger.debug("PIL/Pillow not available, skipping thumbnail creation")
            return
        try:
            with Image.open(file_path) as img:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                thumbnail_path = file_path.parent / f"{file_path.stem}_thumb{file_path.suffix}"
                img.save(thumbnail_path)
        except Exception as e:
            logger.warning(f"Failed to create thumbnail: {e}")

