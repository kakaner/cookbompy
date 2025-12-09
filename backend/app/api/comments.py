from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from math import ceil

from app.database import get_db
from app.models.user import User
from app.models.read import Read
from app.models.semester import Semester
from app.models.comment import Comment, CommentReaction
from app.schemas.comment import (
    CommentCreate,
    CommentResponse,
    CommentListResponse,
    CommentReactionCreate,
    ReactionUsersResponse,
    CommentReactionResponse
)
from app.core.security import get_current_user
from app.services.comment_service import (
    get_comments_for_read,
    get_comments_for_semester,
    create_comment,
    delete_comment,
    toggle_reaction,
    aggregate_reactions,
    format_comment_response
)

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/read/{read_id}", response_model=CommentListResponse)
def get_comments(
    read_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated comments for a read"""
    # Verify read exists
    read = db.query(Read).filter(Read.id == read_id).first()
    if not read:
        raise HTTPException(status_code=404, detail="Read not found")
    
    # Get comments
    comments, total = get_comments_for_read(
        db,
        read_id,
        current_user.id,
        page,
        page_size
    )
    
    # Format responses
    formatted_comments = [
        format_comment_response(db, comment, current_user.id)
        for comment in comments
    ]
    
    total_pages = ceil(total / page_size) if total > 0 else 0
    
    return CommentListResponse(
        items=formatted_comments,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/semester/{semester_id}", response_model=CommentListResponse)
def get_semester_comments(
    semester_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated comments for a semester"""
    # Verify semester exists
    semester = db.query(Semester).filter(Semester.id == semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    
    # Get comments
    comments, total = get_comments_for_semester(
        db,
        semester_id,
        current_user.id,
        page,
        page_size
    )
    
    # Format responses
    formatted_comments = [
        format_comment_response(db, comment, current_user.id)
        for comment in comments
    ]
    
    total_pages = ceil(total / page_size) if total > 0 else 0
    
    return CommentListResponse(
        items=formatted_comments,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment_endpoint(
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new comment on a read or semester"""
    try:
        comment = create_comment(
            db,
            current_user.id,
            comment_data.content,
            read_id=comment_data.read_id,
            semester_id=comment_data.semester_id,
            parent_comment_id=comment_data.parent_comment_id
        )
        
        # Reload with relationships
        if comment.read_id:
            db.refresh(comment, ['user', 'read', 'replies', 'reactions'])
        else:
            db.refresh(comment, ['user', 'semester', 'replies', 'reactions'])
        
        # Format response
        formatted = format_comment_response(db, comment, current_user.id)
        
        # TODO: Trigger notifications (future enhancement)
        # - Notify read/semester author (if commenter != author)
        # - Notify parent comment author (if replying to comment)
        # - Use email/in-app notification system when implemented
        
        return formatted
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment_endpoint(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a comment (soft delete)"""
    # Get comment to find target author
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Get target author (read or semester)
    target_author_id = None
    if comment.read_id:
        read = db.query(Read).filter(Read.id == comment.read_id).first()
        if not read:
            raise HTTPException(status_code=404, detail="Read not found")
        target_author_id = read.user_id
    elif comment.semester_id:
        semester = db.query(Semester).filter(Semester.id == comment.semester_id).first()
        if not semester:
            raise HTTPException(status_code=404, detail="Semester not found")
        target_author_id = semester.user_id
    else:
        raise HTTPException(status_code=400, detail="Comment has no associated read or semester")
    
    try:
        delete_comment(db, comment_id, current_user.id, target_author_id)
        return None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")


@router.post("/{comment_id}/reactions")
def toggle_reaction_endpoint(
    comment_id: int,
    reaction_data: CommentReactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle a reaction on a comment"""
    try:
        reactions, current_user_reactions = toggle_reaction(
            db,
            comment_id,
            current_user.id,
            reaction_data.reaction_type
        )
        return {
            "reactions": reactions,
            "current_user_reactions": current_user_reactions
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{comment_id}/reactions", response_model=ReactionUsersResponse)
def get_reaction_users(
    comment_id: int,
    reaction_type: str = Query(..., description="Reaction type to filter by"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get users who reacted with a specific reaction type"""
    # Verify comment exists
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Get reactions
    query = db.query(CommentReaction).filter(
        CommentReaction.comment_id == comment_id,
        CommentReaction.reaction_type == reaction_type
    ).order_by(CommentReaction.created_at.asc())
    
    total = query.count()
    offset = (page - 1) * page_size
    reactions = query.options(
        # Eager load user relationship
    ).offset(offset).limit(page_size).all()
    
    # Format responses
    from app.schemas.comment import UserBasic
    items = []
    for reaction in reactions:
        items.append(CommentReactionResponse(
            id=reaction.id,
            user=UserBasic(
                id=reaction.user.id,
                username=reaction.user.username,
                display_name=reaction.user.display_name,
                profile_photo_url=getattr(reaction.user, 'profile_photo_url', None)
            ),
            reaction_type=reaction.reaction_type,
            created_at=reaction.created_at
        ))
    
    total_pages = ceil(total / page_size) if total > 0 else 0
    
    return ReactionUsersResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/search", response_model=CommentListResponse)
def search_comments(
    q: str = Query(..., min_length=1, description="Search query"),
    read_id: Optional[int] = Query(None, description="Filter by read ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search comments by content"""
    query = db.query(Comment).filter(
        Comment.is_deleted == False,
        Comment.content.ilike(f"%{q}%")
    )
    
    if read_id:
        query = query.filter(Comment.read_id == read_id)
    if user_id:
        query = query.filter(Comment.user_id == user_id)
    
    total = query.count()
    offset = (page - 1) * page_size
    comments = query.options(
        # Eager load relationships
    ).order_by(Comment.created_at.desc()).offset(offset).limit(page_size).all()
    
    # Format responses (only top-level for search results)
    formatted_comments = [
        format_comment_response(db, comment, current_user.id)
        for comment in comments
        if comment.parent_comment_id is None  # Only show top-level in search
    ]
    
    total_pages = ceil(total / page_size) if total > 0 else 0
    
    return CommentListResponse(
        items=formatted_comments,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

