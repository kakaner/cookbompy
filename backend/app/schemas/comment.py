from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="Comment content (1-1000 characters)")
    parent_comment_id: Optional[int] = None


class CommentCreate(CommentBase):
    read_id: Optional[int] = None
    semester_id: Optional[int] = None
    
    @field_validator('read_id', 'semester_id')
    @classmethod
    def validate_target(cls, v, info):
        # At least one of read_id or semester_id must be provided
        values = info.data
        if not values.get('read_id') and not values.get('semester_id'):
            raise ValueError('Either read_id or semester_id must be provided')
        if values.get('read_id') and values.get('semester_id'):
            raise ValueError('Cannot specify both read_id and semester_id')
        return v


class CommentReactionCreate(BaseModel):
    reaction_type: str = Field(..., description="Reaction type: heart, thumbs_up, laugh, think, target, book, clap")
    
    @field_validator('reaction_type')
    @classmethod
    def validate_reaction_type(cls, v: str) -> str:
        valid_types = ['heart', 'thumbs_up', 'laugh', 'think', 'target', 'book', 'clap']
        if v not in valid_types:
            raise ValueError(f'Reaction type must be one of: {", ".join(valid_types)}')
        return v


class UserBasic(BaseModel):
    """Basic user info for comment responses"""
    id: int
    username: str
    display_name: Optional[str] = None
    profile_photo_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class CommentReactionResponse(BaseModel):
    id: int
    user: UserBasic
    reaction_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    id: int
    read_id: Optional[int] = None
    semester_id: Optional[int] = None
    user_id: int
    parent_comment_id: Optional[int] = None
    content: Optional[str] = None  # None if deleted
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    user: UserBasic
    replies: List['CommentResponse'] = []
    reactions: Dict[str, Dict] = Field(default_factory=dict)  # {reaction_type: {count: int, users: List[int]}}
    current_user_reactions: List[str] = Field(default_factory=list)  # Reaction types current user has
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Update forward reference
CommentResponse.model_rebuild()


class CommentListResponse(BaseModel):
    """Paginated comment list response"""
    items: List[CommentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ReactionUsersResponse(BaseModel):
    """Paginated list of users who reacted"""
    items: List[CommentReactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

