from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AuthorBase(BaseModel):
    """Base author schema"""
    name: str = Field(..., min_length=1, max_length=500)
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    nationality: Optional[str] = Field(None, max_length=100)
    photo_url: Optional[str] = Field(None, max_length=500)
    biography: Optional[str] = None


class AuthorCreate(AuthorBase):
    """Schema for creating an author"""
    pass


class AuthorUpdate(BaseModel):
    """Schema for updating an author (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    nationality: Optional[str] = Field(None, max_length=100)
    photo_url: Optional[str] = Field(None, max_length=500)
    biography: Optional[str] = None


class AuthorResponse(AuthorBase):
    """Schema for author response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

