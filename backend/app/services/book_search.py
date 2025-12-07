import requests
from typing import List, Optional
from app.schemas.book import BookSearchResult
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching external book databases"""
    
    def __init__(self):
        self.google_books_api = "https://www.googleapis.com/books/v1/volumes"
        self.open_library_api = "https://openlibrary.org/search.json"
    
    def search_external(self, query: str, isbn: Optional[str] = None) -> List[BookSearchResult]:
        """
        Search external databases for books
        Priority: Google Books -> Open Library
        """
        results = []
        
        # If ISBN provided, try direct lookup first
        if isbn:
            isbn_clean = isbn.replace("-", "").replace(" ", "")
            # Try Google Books with ISBN
            google_result = self._search_google_books_by_isbn(isbn_clean)
            if google_result:
                results.extend(google_result)
                if len(results) >= 10:  # Limit results
                    return results[:10]
        
        # Search by query
        # Try Google Books
        google_results = self._search_google_books(query)
        if google_results:
            results.extend(google_results)
        
        # Try Open Library if we don't have enough results
        if len(results) < 5:
            open_lib_results = self._search_open_library(query)
            if open_lib_results:
                results.extend(open_lib_results)
        
        # Remove duplicates based on ISBN
        seen_isbns = set()
        unique_results = []
        for result in results:
            isbn_key = result.isbn_13 or result.isbn_10 or ""
            if isbn_key and isbn_key in seen_isbns:
                continue
            if isbn_key:
                seen_isbns.add(isbn_key)
            unique_results.append(result)
            if len(unique_results) >= 20:  # Limit to 20 results
                break
        
        return unique_results
    
    def _search_google_books(self, query: str) -> List[BookSearchResult]:
        """Search Google Books API"""
        try:
            params = {
                "q": query,
                "maxResults": 20,
                "fields": "items(id,volumeInfo(title,authors,industryIdentifiers,publishedDate,publisher,pageCount,description,categories,imageLinks))"
            }
            response = requests.get(self.google_books_api, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if "items" in data:
                for item in data["items"]:
                    volume_info = item.get("volumeInfo", {})
                    result = self._normalize_google_result(volume_info)
                    if result:
                        results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Google Books search error: {e}")
            return []
    
    def _search_google_books_by_isbn(self, isbn: str) -> List[BookSearchResult]:
        """Search Google Books by ISBN"""
        try:
            params = {
                "q": f"isbn:{isbn}",
                "maxResults": 5,
                "fields": "items(volumeInfo(title,authors,industryIdentifiers,publishedDate,publisher,pageCount,description,categories,imageLinks))"
            }
            response = requests.get(self.google_books_api, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if "items" in data:
                for item in data["items"]:
                    volume_info = item.get("volumeInfo", {})
                    result = self._normalize_google_result(volume_info)
                    if result:
                        results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Google Books ISBN search error: {e}")
            return []
    
    def _search_open_library(self, query: str) -> List[BookSearchResult]:
        """Search Open Library API"""
        try:
            params = {
                "q": query,
                "limit": 20,
                "fields": "title,author_name,isbn,publish_date,publisher,number_of_pages_median,subject,cover_i"
            }
            response = requests.get(self.open_library_api, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if "docs" in data:
                for doc in data["docs"]:
                    result = self._normalize_open_library_result(doc)
                    if result:
                        results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Open Library search error: {e}")
            return []
    
    def _normalize_google_result(self, volume_info: dict) -> Optional[BookSearchResult]:
        """Normalize Google Books result to BookSearchResult"""
        try:
            title = volume_info.get("title", "")
            if not title:
                return None
            
            authors = volume_info.get("authors", [])
            author = ", ".join(authors) if authors else "Unknown"
            
            # Extract ISBNs
            isbn_10 = None
            isbn_13 = None
            for identifier in volume_info.get("industryIdentifiers", []):
                id_type = identifier.get("type", "")
                id_value = identifier.get("identifier", "")
                if id_type == "ISBN_10":
                    isbn_10 = id_value
                elif id_type == "ISBN_13":
                    isbn_13 = id_value
            
            # Extract publication year
            published_date = volume_info.get("publishedDate", "")
            publication_year = None
            if published_date:
                try:
                    # Try to extract year (format can be "2024", "2024-01", "2024-01-15")
                    year_str = published_date.split("-")[0]
                    publication_year = int(year_str)
                except (ValueError, IndexError):
                    pass
            
            # Extract page count
            page_count = volume_info.get("pageCount")
            
            # Extract description
            description = volume_info.get("description", "")
            
            # Extract genres/categories
            categories = volume_info.get("categories", [])
            genres = categories if categories else None
            
            # Extract cover image
            image_links = volume_info.get("imageLinks", {})
            cover_url = image_links.get("thumbnail") or image_links.get("smallThumbnail")
            if cover_url:
                # Replace http with https and remove zoom parameter for larger image
                cover_url = cover_url.replace("http://", "https://").replace("&zoom=1", "").replace("zoom=1", "")
            
            return BookSearchResult(
                title=title,
                author=author,
                isbn_10=isbn_10,
                isbn_13=isbn_13,
                publication_year=publication_year,
                publisher=volume_info.get("publisher"),
                page_count=page_count,
                description=description,
                genres=genres,
                cover_url=cover_url,
                source="google_books"
            )
        except Exception as e:
            logger.error(f"Error normalizing Google Books result: {e}")
            return None
    
    def _normalize_open_library_result(self, doc: dict) -> Optional[BookSearchResult]:
        """Normalize Open Library result to BookSearchResult"""
        try:
            title = doc.get("title", "")
            if not title:
                return None
            
            author_names = doc.get("author_name", [])
            author = ", ".join(author_names) if author_names else "Unknown"
            
            # Extract ISBNs
            isbns = doc.get("isbn", [])
            isbn_10 = None
            isbn_13 = None
            for isbn in isbns:
                if len(isbn) == 10:
                    isbn_10 = isbn
                elif len(isbn) == 13:
                    isbn_13 = isbn
            
            # Extract publication year
            publish_dates = doc.get("publish_date", [])
            publication_year = None
            if publish_dates:
                try:
                    # Try to extract year from first date
                    year_str = str(publish_dates[0]).split()[-1]  # Get last part (usually year)
                    publication_year = int(year_str)
                except (ValueError, IndexError):
                    pass
            
            # Extract page count
            page_count = doc.get("number_of_pages_median")
            
            # Extract genres/subjects
            subjects = doc.get("subject", [])
            genres = subjects[:5] if subjects else None  # Limit to 5
            
            # Extract cover image
            cover_i = doc.get("cover_i")
            cover_url = None
            if cover_i:
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_i}-L.jpg"
            
            return BookSearchResult(
                title=title,
                author=author,
                isbn_10=isbn_10,
                isbn_13=isbn_13,
                publication_year=publication_year,
                publisher=doc.get("publisher", [None])[0] if doc.get("publisher") else None,
                page_count=page_count,
                description=None,  # Open Library doesn't provide descriptions in search results
                genres=genres,
                cover_url=cover_url,
                source="open_library"
            )
        except Exception as e:
            logger.error(f"Error normalizing Open Library result: {e}")
            return None

