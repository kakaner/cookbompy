from sqlalchemy.orm import Session
from app.models.author import Author
from typing import Optional


def normalize_author_name(name: str) -> str:
    """
    Normalize author name for duplicate detection and matching.
    
    This handles:
    - Case insensitivity
    - Whitespace normalization
    - Common name variations
    """
    if not name:
        return ""
    
    # Convert to lowercase and strip whitespace
    normalized = name.lower().strip()
    
    # Remove extra spaces
    normalized = " ".join(normalized.split())
    
    # Handle common variations (e.g., "Jr.", "Sr.", "III")
    # Remove periods from common suffixes
    normalized = normalized.replace(" jr.", " jr").replace(" sr.", " sr")
    normalized = normalized.replace(" iii", "").replace(" ii", "")
    
    return normalized


def find_or_create_author(db: Session, author_name: str) -> Author:
    """
    Find existing author by name (with normalization) or create a new one.
    
    Args:
        db: Database session
        author_name: Author name string
        
    Returns:
        Author entity
    """
    if not author_name or not author_name.strip():
        raise ValueError("Author name cannot be empty")
    
    normalized = normalize_author_name(author_name)
    
    # Try to find existing author by normalized name
    author = db.query(Author).filter(Author.normalized_name == normalized).first()
    
    if author:
        return author
    
    # Try exact match (case-insensitive)
    author = db.query(Author).filter(Author.name.ilike(author_name.strip())).first()
    if author:
        return author
    
    # Create new author
    author = Author(
        name=author_name.strip(),
        normalized_name=normalized
    )
    db.add(author)
    db.flush()  # Flush to get ID without committing
    
    return author


def get_author_by_id(db: Session, author_id: int) -> Optional[Author]:
    """Get author by ID"""
    return db.query(Author).filter(Author.id == author_id).first()


def search_authors(db: Session, query: str, limit: int = 10) -> list[Author]:
    """
    Search authors by name (case-insensitive partial match).
    
    Args:
        db: Database session
        query: Search query string
        limit: Maximum number of results
        
    Returns:
        List of Author entities
    """
    if not query:
        return []
    
    search_term = f"%{query.lower()}%"
    
    authors = (
        db.query(Author)
        .filter(
            Author.name.ilike(search_term) |
            Author.normalized_name.ilike(search_term)
        )
        .limit(limit)
        .all()
    )
    
    return authors

