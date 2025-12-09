from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.services.file_upload import FileUploadService


router = APIRouter(prefix="/users", tags=["users"])

file_upload_service = FileUploadService()


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences"""
    display_name: Optional[str] = Field(None, max_length=100)
    default_book_format: Optional[str] = Field(None, max_length=50)  # Format enum value as string
    color_theme: Optional[str] = Field(None, max_length=50)
    default_page_size: Optional[int] = Field(None, ge=25, le=200)
    default_home_page: Optional[str] = Field(None, description="Default home page: library, semesters, or statistics")


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    username: str
    email: str
    display_name: Optional[str] = None
    is_active: bool
    profile_photo_url: Optional[str] = None
    default_book_format: Optional[str] = None
    color_theme: Optional[str] = None
    default_page_size: Optional[int] = None
    default_home_page: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile and preferences"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        display_name=current_user.display_name,
        is_active=current_user.is_active,
        profile_photo_url=current_user.profile_photo_url,
        default_book_format=current_user.default_book_format,
        color_theme=current_user.color_theme,
        default_page_size=current_user.default_page_size,
        default_home_page=current_user.default_home_page or 'library'
    )


@router.put("/me", response_model=UserResponse)
def update_user_preferences(
    preferences: UserPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user's preferences"""
    update_data = preferences.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        display_name=current_user.display_name,
        is_active=current_user.is_active,
        profile_photo_url=current_user.profile_photo_url,
        default_book_format=current_user.default_book_format,
        color_theme=current_user.color_theme,
        default_page_size=current_user.default_page_size,
        default_home_page=current_user.default_home_page or 'library'
    )


@router.post("/me/photo", response_model=UserResponse)
async def upload_profile_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a profile photo"""
    # Upload the file
    photo_url = await file_upload_service.upload_profile_photo(file, current_user.id)
    
    # Update user record
    current_user.profile_photo_url = photo_url
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        display_name=current_user.display_name,
        is_active=current_user.is_active,
        profile_photo_url=current_user.profile_photo_url,
        default_book_format=current_user.default_book_format,
        color_theme=current_user.color_theme,
        default_page_size=current_user.default_page_size,
        default_home_page=current_user.default_home_page or 'library'
    )


@router.delete("/me/photo", response_model=UserResponse)
def delete_profile_photo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete the current profile photo"""
    current_user.profile_photo_url = None
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        display_name=current_user.display_name,
        is_active=current_user.is_active,
        profile_photo_url=current_user.profile_photo_url,
        default_book_format=current_user.default_book_format,
        color_theme=current_user.color_theme,
        default_page_size=current_user.default_page_size,
        default_home_page=current_user.default_home_page or 'library'
    )

