from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Dict, Optional
from datetime import datetime, timezone

from app.models.comment import Comment, CommentReaction
from app.models.read import Read
from app.models.semester import Semester
from app.models.user import User


def get_comments_for_read(
    db: Session,
    read_id: int,
    current_user_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20
) -> tuple[List[Comment], int]:
    """
    Get paginated top-level comments for a read with their replies.
    Returns (comments, total_count)
    """
    # Get total count of top-level comments
    total = db.query(Comment).filter(
        Comment.read_id == read_id,
        Comment.parent_comment_id.is_(None),
        Comment.is_deleted == False
    ).count()
    
    # Get top-level comments with eager loading
    offset = (page - 1) * page_size
    top_level_comments = db.query(Comment).options(
        joinedload(Comment.user),
        joinedload(Comment.replies).joinedload(Comment.user),
        joinedload(Comment.reactions).joinedload(CommentReaction.user)
    ).filter(
        Comment.read_id == read_id,
        Comment.parent_comment_id.is_(None),
        Comment.is_deleted == False
    ).order_by(Comment.created_at.asc()).offset(offset).limit(page_size).all()
    
    # Load replies for each top-level comment (max 1 level deep)
    for comment in top_level_comments:
        comment.replies = [
            reply for reply in comment.replies 
            if not reply.is_deleted
        ]
        # Sort replies chronologically
        comment.replies.sort(key=lambda r: r.created_at)
    
    return top_level_comments, total


def get_comments_for_semester(
    db: Session,
    semester_id: int,
    current_user_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20
) -> tuple[List[Comment], int]:
    """
    Get paginated top-level comments for a semester with their replies.
    Returns (comments, total_count)
    """
    # Get total count of top-level comments
    total = db.query(Comment).filter(
        Comment.semester_id == semester_id,
        Comment.parent_comment_id.is_(None),
        Comment.is_deleted == False
    ).count()
    
    # Get top-level comments with eager loading
    offset = (page - 1) * page_size
    top_level_comments = db.query(Comment).options(
        joinedload(Comment.user),
        joinedload(Comment.replies).joinedload(Comment.user),
        joinedload(Comment.reactions).joinedload(CommentReaction.user)
    ).filter(
        Comment.semester_id == semester_id,
        Comment.parent_comment_id.is_(None),
        Comment.is_deleted == False
    ).order_by(Comment.created_at.asc()).offset(offset).limit(page_size).all()
    
    # Load replies for each top-level comment (max 1 level deep)
    for comment in top_level_comments:
        comment.replies = [
            reply for reply in comment.replies 
            if not reply.is_deleted
        ]
        # Sort replies chronologically
        comment.replies.sort(key=lambda r: r.created_at)
    
    return top_level_comments, total


def create_comment(
    db: Session,
    user_id: int,
    content: str,
    read_id: Optional[int] = None,
    semester_id: Optional[int] = None,
    parent_comment_id: Optional[int] = None
) -> Comment:
    """
    Create a new comment. Validates threading constraints.
    Either read_id or semester_id must be provided.
    """
    # Validate that exactly one target is provided
    if not read_id and not semester_id:
        raise ValueError("Either read_id or semester_id must be provided")
    if read_id and semester_id:
        raise ValueError("Cannot specify both read_id and semester_id")
    
    # Validate target exists
    if read_id:
        read = db.query(Read).filter(Read.id == read_id).first()
        if not read:
            raise ValueError("Read not found")
        target_id = read_id
        target_type = 'read'
    else:
        semester = db.query(Semester).filter(Semester.id == semester_id).first()
        if not semester:
            raise ValueError("Semester not found")
        target_id = semester_id
        target_type = 'semester'
    
    # If replying, validate parent comment
    if parent_comment_id:
        parent = db.query(Comment).filter(
            Comment.id == parent_comment_id,
            Comment.is_deleted == False
        ).first()
        if not parent:
            raise ValueError("Parent comment not found or deleted")
        
        # Ensure parent is for the same target
        if target_type == 'read' and parent.read_id != target_id:
            raise ValueError("Parent comment is not for this read")
        if target_type == 'semester' and parent.semester_id != target_id:
            raise ValueError("Parent comment is not for this semester")
        
        # Ensure parent is top-level (max 2 levels)
        if parent.parent_comment_id is not None:
            raise ValueError("Cannot reply to a reply (max 2 levels)")
    
    # Create comment
    comment = Comment(
        read_id=read_id,
        semester_id=semester_id,
        user_id=user_id,
        parent_comment_id=parent_comment_id,
        content=content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # Eager load relationships
    if read_id:
        db.refresh(comment, ['user', 'read'])
    else:
        db.refresh(comment, ['user', 'semester'])
    
    return comment


def delete_comment(
    db: Session,
    comment_id: int,
    user_id: int,
    target_author_id: int
) -> bool:
    """
    Soft delete a comment. Returns True if deleted, False if not found.
    Permission: comment author OR target (read/semester) author
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return False
    
    # Check permissions
    if comment.user_id != user_id and target_author_id != user_id:
        raise PermissionError("Not authorized to delete this comment")
    
    # Soft delete
    comment.is_deleted = True
    comment.deleted_at = datetime.now(timezone.utc)
    db.commit()
    
    return True


def toggle_reaction(
    db: Session,
    comment_id: int,
    user_id: int,
    reaction_type: str
) -> Dict[str, int]:
    """
    Toggle a reaction on a comment. Returns updated reaction counts.
    """
    # Validate comment exists and is not deleted
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.is_deleted == False
    ).first()
    if not comment:
        raise ValueError("Comment not found or deleted")
    
    # Check if reaction exists
    existing = db.query(CommentReaction).filter(
        CommentReaction.comment_id == comment_id,
        CommentReaction.user_id == user_id,
        CommentReaction.reaction_type == reaction_type
    ).first()
    
    if existing:
        # Remove reaction
        db.delete(existing)
    else:
        # Add reaction
        reaction = CommentReaction(
            comment_id=comment_id,
            user_id=user_id,
            reaction_type=reaction_type
        )
        db.add(reaction)
    
    db.commit()
    
    # Get updated counts
    return aggregate_reactions(db, comment_id, user_id)


def aggregate_reactions(
    db: Session,
    comment_id: int,
    current_user_id: Optional[int] = None
) -> Dict[str, Dict]:
    """
    Aggregate reactions for a comment.
    Returns: {
        'heart': {'count': 5, 'users': [1, 2, 3]},
        'thumbs_up': {'count': 3, 'users': [4, 5]},
        ...
    }
    Also returns current_user_reactions list.
    """
    reactions = db.query(CommentReaction).filter(
        CommentReaction.comment_id == comment_id
    ).all()
    
    # Group by reaction type
    aggregated = {}
    current_user_reactions = []
    
    for reaction in reactions:
        if reaction.reaction_type not in aggregated:
            aggregated[reaction.reaction_type] = {
                'count': 0,
                'users': []
            }
        aggregated[reaction.reaction_type]['count'] += 1
        aggregated[reaction.reaction_type]['users'].append(reaction.user_id)
        
        if current_user_id and reaction.user_id == current_user_id:
            current_user_reactions.append(reaction.reaction_type)
    
    return aggregated, current_user_reactions


def format_comment_response(
    db: Session,
    comment: Comment,
    current_user_id: Optional[int] = None
) -> Dict:
    """
    Format a comment (and its replies) for API response.
    Includes aggregated reactions.
    """
    # Aggregate reactions
    reactions_dict, current_user_reactions = aggregate_reactions(
        db,
        comment.id,
        current_user_id
    )
    
    # Format user
    user_data = {
        'id': comment.user.id,
        'username': comment.user.username,
        'display_name': getattr(comment.user, 'display_name', None),
        'profile_photo_url': getattr(comment.user, 'profile_photo_url', None)
    }
    
    # Format comment
    result = {
        'id': comment.id,
        'read_id': comment.read_id,
        'semester_id': comment.semester_id,
        'user_id': comment.user_id,
        'parent_comment_id': comment.parent_comment_id,
        'content': None if comment.is_deleted else comment.content,
        'is_deleted': comment.is_deleted,
        'deleted_at': comment.deleted_at.isoformat() if comment.deleted_at else None,
        'user': user_data,
        'replies': [],
        'reactions': reactions_dict,
        'current_user_reactions': current_user_reactions,
        'created_at': comment.created_at,
        'updated_at': comment.updated_at
    }
    
    # Format replies (max 1 level)
    if comment.replies:
        result['replies'] = [
            format_comment_response(db, reply, current_user_id)
            for reply in sorted(comment.replies, key=lambda r: r.created_at)
            if not reply.is_deleted
        ]
    
    return result

