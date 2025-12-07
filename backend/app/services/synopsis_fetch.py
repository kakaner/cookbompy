import requests
from typing import Optional, Tuple
from app.core.enums import DescriptionSource
import logging

logger = logging.getLogger(__name__)


class SynopsisFetchService:
    """Service for fetching book synopsis from external sources with fallback hierarchy"""
    
    def __init__(self):
        self.google_books_api = "https://www.googleapis.com/books/v1/volumes"
    
    def fetch_synopsis(self, isbn: Optional[str] = None, title: Optional[str] = None, author: Optional[str] = None) -> Tuple[Optional[str], Optional[DescriptionSource]]:
        """
        Fetch synopsis with fallback hierarchy:
        1. Goodreads (if API available)
        2. Google Books
        3. Amazon (if API available)
        4. Wikipedia
        
        Returns: (synopsis_text, source) or (None, None) if not found
        """
        # Try Goodreads first (requires API key - skip for now, implement later)
        # goodreads_synopsis = self._fetch_from_goodreads(isbn, title, author)
        # if goodreads_synopsis:
        #     return goodreads_synopsis, DescriptionSource.GOODREADS
        
        # Try Google Books
        google_synopsis = self._fetch_from_google_books(isbn, title, author)
        if google_synopsis:
            return google_synopsis, DescriptionSource.GOOGLE_BOOKS
        
        # Try Amazon (requires API key - skip for now, implement later)
        # amazon_synopsis = self._fetch_from_amazon(isbn)
        # if amazon_synopsis:
        #     return amazon_synopsis, DescriptionSource.AMAZON
        
        # Try Wikipedia
        wikipedia_synopsis = self._fetch_from_wikipedia(title, author)
        if wikipedia_synopsis:
            return wikipedia_synopsis, DescriptionSource.WIKIPEDIA
        
        return None, None
    
    def _fetch_from_google_books(self, isbn: Optional[str] = None, title: Optional[str] = None, author: Optional[str] = None) -> Optional[str]:
        """Fetch synopsis from Google Books API"""
        try:
            # Build query
            query_parts = []
            if isbn:
                query_parts.append(f"isbn:{isbn.replace('-', '').replace(' ', '')}")
            if title:
                query_parts.append(f"intitle:{title}")
            if author:
                query_parts.append(f"inauthor:{author}")
            
            if not query_parts:
                return None
            
            query = "+".join(query_parts)
            
            params = {
                "q": query,
                "maxResults": 1,
                "fields": "items(volumeInfo(description))"
            }
            
            response = requests.get(self.google_books_api, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if "items" in data and len(data["items"]) > 0:
                volume_info = data["items"][0].get("volumeInfo", {})
                description = volume_info.get("description", "")
                if description:
                    # Clean up HTML if present
                    description = description.replace("<br>", "\n").replace("<p>", "").replace("</p>", "\n")
                    description = description.replace("<i>", "").replace("</i>", "")
                    description = description.replace("<b>", "").replace("</b>", "")
                    # Remove extra whitespace
                    description = " ".join(description.split())
                    return description[:2000]  # Limit length
            
            return None
        except Exception as e:
            logger.error(f"Google Books synopsis fetch error: {e}")
            return None
    
    def _fetch_from_wikipedia(self, title: Optional[str] = None, author: Optional[str] = None) -> Optional[str]:
        """Fetch synopsis from Wikipedia"""
        if not title:
            return None
        
        try:
            # Search Wikipedia for the book
            search_query = title
            if author:
                search_query = f"{title} {author}"
            
            search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(title)
            
            response = requests.get(search_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                extract = data.get("extract", "")
                if extract and len(extract) > 100:  # Only return if substantial content
                    # Try to find plot summary section
                    # For now, return the extract (first paragraph)
                    return extract[:2000]  # Limit length
            
            return None
        except Exception as e:
            logger.error(f"Wikipedia synopsis fetch error: {e}")
            return None
    
    def _fetch_from_goodreads(self, isbn: Optional[str] = None, title: Optional[str] = None, author: Optional[str] = None) -> Optional[str]:
        """Fetch synopsis from Goodreads API (requires API key)"""
        # TODO: Implement when Goodreads API key is available
        return None
    
    def _fetch_from_amazon(self, isbn: Optional[str] = None) -> Optional[str]:
        """Fetch synopsis from Amazon Product API (requires API key)"""
        # TODO: Implement when Amazon API key is available
        return None

