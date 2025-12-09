"""
Script to create dummy library data for user 'kagua'
Creates ~75 books with reads spread over the past 10 years
"""
import sys
import os
from datetime import date, datetime, timedelta
import random
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models.user import User
from app.models.book import Book
from app.models.read import Read
from app.core.enums import Format, BookType, ReadStatus, DescriptionSource
from app.core.security import get_password_hash
from app.services.point_calculator import PointCalculator

# Sample book data
SAMPLE_BOOKS = [
    # Fiction
    {"title": "The Remains of the Day", "author": "Kazuo Ishiguro", "book_type": BookType.FICTION, "page_count": 245, "format": Format.PAPERBACK},
    {"title": "Beloved", "author": "Toni Morrison", "book_type": BookType.FICTION, "page_count": 324, "format": Format.HARDCOVER},
    {"title": "The Handmaid's Tale", "author": "Margaret Atwood", "book_type": BookType.FICTION, "page_count": 311, "format": Format.PAPERBACK},
    {"title": "One Hundred Years of Solitude", "author": "Gabriel García Márquez", "book_type": BookType.FICTION, "page_count": 417, "format": Format.PAPERBACK},
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "book_type": BookType.FICTION, "page_count": 180, "format": Format.HARDCOVER},
    {"title": "To Kill a Mockingbird", "author": "Harper Lee", "book_type": BookType.FICTION, "page_count": 281, "format": Format.PAPERBACK},
    {"title": "1984", "author": "George Orwell", "book_type": BookType.FICTION, "page_count": 328, "format": Format.PAPERBACK},
    {"title": "Pride and Prejudice", "author": "Jane Austen", "book_type": BookType.FICTION, "page_count": 432, "format": Format.HARDCOVER},
    {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "book_type": BookType.FICTION, "page_count": 234, "format": Format.PAPERBACK},
    {"title": "Brave New World", "author": "Aldous Huxley", "book_type": BookType.FICTION, "page_count": 311, "format": Format.PAPERBACK},
    {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "book_type": BookType.FICTION, "page_count": 1178, "format": Format.HARDCOVER},
    {"title": "Dune", "author": "Frank Herbert", "book_type": BookType.FICTION, "page_count": 688, "format": Format.PAPERBACK},
    {"title": "The Road", "author": "Cormac McCarthy", "book_type": BookType.FICTION, "page_count": 287, "format": Format.PAPERBACK},
    {"title": "The Kite Runner", "author": "Khaled Hosseini", "book_type": BookType.FICTION, "page_count": 371, "format": Format.PAPERBACK},
    {"title": "Life of Pi", "author": "Yann Martel", "book_type": BookType.FICTION, "page_count": 319, "format": Format.PAPERBACK},
    {"title": "The Secret History", "author": "Donna Tartt", "book_type": BookType.FICTION, "page_count": 559, "format": Format.PAPERBACK},
    {"title": "The Goldfinch", "author": "Donna Tartt", "book_type": BookType.FICTION, "page_count": 771, "format": Format.HARDCOVER},
    {"title": "Station Eleven", "author": "Emily St. John Mandel", "book_type": BookType.FICTION, "page_count": 333, "format": Format.PAPERBACK},
    {"title": "The Overstory", "author": "Richard Powers", "book_type": BookType.FICTION, "page_count": 502, "format": Format.PAPERBACK},
    {"title": "Circe", "author": "Madeline Miller", "book_type": BookType.FICTION, "page_count": 393, "format": Format.PAPERBACK},
    
    # Nonfiction
    {"title": "Sapiens", "author": "Yuval Noah Harari", "book_type": BookType.NONFICTION, "page_count": 443, "format": Format.PAPERBACK},
    {"title": "Educated", "author": "Tara Westover", "book_type": BookType.NONFICTION, "page_count": 334, "format": Format.HARDCOVER},
    {"title": "The Immortal Life of Henrietta Lacks", "author": "Rebecca Skloot", "book_type": BookType.NONFICTION, "page_count": 381, "format": Format.PAPERBACK},
    {"title": "Becoming", "author": "Michelle Obama", "book_type": BookType.NONFICTION, "page_count": 426, "format": Format.HARDCOVER},
    {"title": "The Sixth Extinction", "author": "Elizabeth Kolbert", "book_type": BookType.NONFICTION, "page_count": 319, "format": Format.PAPERBACK},
    {"title": "The Warmth of Other Suns", "author": "Isabel Wilkerson", "book_type": BookType.NONFICTION, "page_count": 622, "format": Format.PAPERBACK},
    {"title": "Between the World and Me", "author": "Ta-Nehisi Coates", "book_type": BookType.NONFICTION, "page_count": 152, "format": Format.PAPERBACK},
    {"title": "The Body Keeps the Score", "author": "Bessel van der Kolk", "book_type": BookType.NONFICTION, "page_count": 464, "format": Format.PAPERBACK},
    {"title": "Thinking, Fast and Slow", "author": "Daniel Kahneman", "book_type": BookType.NONFICTION, "page_count": 499, "format": Format.PAPERBACK},
    {"title": "The Gene", "author": "Siddhartha Mukherjee", "book_type": BookType.NONFICTION, "page_count": 592, "format": Format.HARDCOVER},
    
    # YA
    {"title": "The Hunger Games", "author": "Suzanne Collins", "book_type": BookType.YA, "page_count": 374, "format": Format.PAPERBACK},
    {"title": "The Fault in Our Stars", "author": "John Green", "book_type": BookType.YA, "page_count": 313, "format": Format.PAPERBACK},
    {"title": "Eleanor & Park", "author": "Rainbow Rowell", "book_type": BookType.YA, "page_count": 325, "format": Format.PAPERBACK},
    {"title": "The Hate U Give", "author": "Angie Thomas", "book_type": BookType.YA, "page_count": 444, "format": Format.PAPERBACK},
    {"title": "Six of Crows", "author": "Leigh Bardugo", "book_type": BookType.YA, "page_count": 465, "format": Format.PAPERBACK},
    {"title": "The Book Thief", "author": "Markus Zusak", "book_type": BookType.YA, "page_count": 552, "format": Format.PAPERBACK},
    
    # More variety
    {"title": "Mongrels", "author": "Stephen Graham Jones", "book_type": BookType.FICTION, "page_count": 304, "format": Format.PAPERBACK},
    {"title": "Creation Lake", "author": "Rachel Kushner", "book_type": BookType.FICTION, "page_count": 418, "format": Format.HARDCOVER},
    {"title": "Picnic at Hanging Rock", "author": "Joan Lindsay", "book_type": BookType.FICTION, "page_count": 213, "format": Format.PAPERBACK},
    {"title": "The Buried Giant", "author": "Kazuo Ishiguro", "book_type": BookType.FICTION, "page_count": 317, "format": Format.PAPERBACK},
    {"title": "Klara and the Sun", "author": "Kazuo Ishiguro", "book_type": BookType.FICTION, "page_count": 303, "format": Format.PAPERBACK},
    {"title": "Never Let Me Go", "author": "Kazuo Ishiguro", "book_type": BookType.FICTION, "page_count": 288, "format": Format.PAPERBACK},
    {"title": "The Testaments", "author": "Margaret Atwood", "book_type": BookType.FICTION, "page_count": 419, "format": Format.HARDCOVER},
    {"title": "The Seven Husbands of Evelyn Hugo", "author": "Taylor Jenkins Reid", "book_type": BookType.FICTION, "page_count": 389, "format": Format.PAPERBACK},
    {"title": "Project Hail Mary", "author": "Andy Weir", "book_type": BookType.FICTION, "page_count": 476, "format": Format.PAPERBACK},
    {"title": "The Midnight Library", "author": "Matt Haig", "book_type": BookType.FICTION, "page_count": 288, "format": Format.PAPERBACK},
    {"title": "Piranesi", "author": "Susanna Clarke", "book_type": BookType.FICTION, "page_count": 245, "format": Format.PAPERBACK},
    {"title": "The Invisible Life of Addie LaRue", "author": "V.E. Schwab", "book_type": BookType.FICTION, "page_count": 444, "format": Format.PAPERBACK},
    {"title": "The Song of Achilles", "author": "Madeline Miller", "book_type": BookType.FICTION, "page_count": 378, "format": Format.PAPERBACK},
    {"title": "The Seven Deaths of Evelyn Hardcastle", "author": "Stuart Turton", "book_type": BookType.FICTION, "page_count": 432, "format": Format.PAPERBACK},
    {"title": "The Thursday Murder Club", "author": "Richard Osman", "book_type": BookType.FICTION, "page_count": 382, "format": Format.PAPERBACK},
    {"title": "Where the Crawdads Sing", "author": "Delia Owens", "book_type": BookType.FICTION, "page_count": 368, "format": Format.PAPERBACK},
    {"title": "The Silent Patient", "author": "Alex Michaelides", "book_type": BookType.FICTION, "page_count": 323, "format": Format.PAPERBACK},
    {"title": "Normal People", "author": "Sally Rooney", "book_type": BookType.FICTION, "page_count": 266, "format": Format.PAPERBACK},
    {"title": "Conversations with Friends", "author": "Sally Rooney", "book_type": BookType.FICTION, "page_count": 304, "format": Format.PAPERBACK},
    {"title": "The Vanishing Half", "author": "Brit Bennett", "book_type": BookType.FICTION, "page_count": 343, "format": Format.PAPERBACK},
    {"title": "The Glass Hotel", "author": "Emily St. John Mandel", "book_type": BookType.FICTION, "page_count": 303, "format": Format.PAPERBACK},
    {"title": "The Dutch House", "author": "Ann Patchett", "book_type": BookType.FICTION, "page_count": 337, "format": Format.HARDCOVER},
    {"title": "Olive Kitteridge", "author": "Elizabeth Strout", "book_type": BookType.FICTION, "page_count": 270, "format": Format.PAPERBACK},
    {"title": "My Year of Rest and Relaxation", "author": "Ottessa Moshfegh", "book_type": BookType.FICTION, "page_count": 288, "format": Format.PAPERBACK},
    {"title": "Eileen", "author": "Ottessa Moshfegh", "book_type": BookType.FICTION, "page_count": 260, "format": Format.PAPERBACK},
    {"title": "Severance", "author": "Ling Ma", "book_type": BookType.FICTION, "page_count": 291, "format": Format.PAPERBACK},
    {"title": "There There", "author": "Tommy Orange", "book_type": BookType.FICTION, "page_count": 294, "format": Format.PAPERBACK},
    {"title": "The Water Dancer", "author": "Ta-Nehisi Coates", "book_type": BookType.FICTION, "page_count": 403, "format": Format.HARDCOVER},
    {"title": "Deacon King Kong", "author": "James McBride", "book_type": BookType.FICTION, "page_count": 384, "format": Format.PAPERBACK},
    {"title": "The Nickel Boys", "author": "Colson Whitehead", "book_type": BookType.FICTION, "page_count": 213, "format": Format.PAPERBACK},
    {"title": "The Underground Railroad", "author": "Colson Whitehead", "book_type": BookType.FICTION, "page_count": 306, "format": Format.PAPERBACK},
    {"title": "Exit West", "author": "Mohsin Hamid", "book_type": BookType.FICTION, "page_count": 231, "format": Format.PAPERBACK},
    {"title": "Lincoln in the Bardo", "author": "George Saunders", "book_type": BookType.FICTION, "page_count": 343, "format": Format.HARDCOVER},
    {"title": "A Little Life", "author": "Hanya Yanagihara", "book_type": BookType.FICTION, "page_count": 720, "format": Format.PAPERBACK},
    {"title": "The Sympathizer", "author": "Viet Thanh Nguyen", "book_type": BookType.FICTION, "page_count": 371, "format": Format.PAPERBACK},
    {"title": "All the Light We Cannot See", "author": "Anthony Doerr", "book_type": BookType.FICTION, "page_count": 531, "format": Format.PAPERBACK},
    {"title": "The Orphan Master's Son", "author": "Adam Johnson", "book_type": BookType.FICTION, "page_count": 443, "format": Format.PAPERBACK},
    {"title": "A Visit from the Goon Squad", "author": "Jennifer Egan", "book_type": BookType.FICTION, "page_count": 274, "format": Format.PAPERBACK},
    {"title": "The Brief Wondrous Life of Oscar Wao", "author": "Junot Díaz", "book_type": BookType.FICTION, "page_count": 335, "format": Format.PAPERBACK},
    {"title": "The Known World", "author": "Edward P. Jones", "book_type": BookType.FICTION, "page_count": 388, "format": Format.PAPERBACK},
    {"title": "Middlesex", "author": "Jeffrey Eugenides", "book_type": BookType.FICTION, "page_count": 529, "format": Format.PAPERBACK},
    {"title": "The Corrections", "author": "Jonathan Franzen", "book_type": BookType.FICTION, "page_count": 568, "format": Format.HARDCOVER},
    {"title": "White Teeth", "author": "Zadie Smith", "book_type": BookType.FICTION, "page_count": 448, "format": Format.PAPERBACK},
    {"title": "The Amazing Adventures of Kavalier & Clay", "author": "Michael Chabon", "book_type": BookType.FICTION, "page_count": 636, "format": Format.PAPERBACK},
    {"title": "Interpreter of Maladies", "author": "Jhumpa Lahiri", "book_type": BookType.FICTION, "page_count": 198, "format": Format.PAPERBACK},
    {"title": "The Hours", "author": "Michael Cunningham", "book_type": BookType.FICTION, "page_count": 226, "format": Format.PAPERBACK},
    {"title": "The English Patient", "author": "Michael Ondaatje", "book_type": BookType.FICTION, "page_count": 302, "format": Format.PAPERBACK},
    {"title": "Atonement", "author": "Ian McEwan", "book_type": BookType.FICTION, "page_count": 351, "format": Format.PAPERBACK},
    {"title": "The Blind Assassin", "author": "Margaret Atwood", "book_type": BookType.FICTION, "page_count": 521, "format": Format.PAPERBACK},
    {"title": "The Shipping News", "author": "E. Annie Proulx", "book_type": BookType.FICTION, "page_count": 337, "format": Format.PAPERBACK},
    {"title": "Possession", "author": "A.S. Byatt", "book_type": BookType.FICTION, "page_count": 555, "format": Format.PAPERBACK},
    {"title": "The Remains of the Day", "author": "Kazuo Ishiguro", "book_type": BookType.FICTION, "page_count": 245, "format": Format.PAPERBACK},  # Overlap book
    {"title": "Mongrels", "author": "Stephen Graham Jones", "book_type": BookType.FICTION, "page_count": 304, "format": Format.PAPERBACK},  # Overlap book
    {"title": "Creation Lake", "author": "Rachel Kushner", "book_type": BookType.FICTION, "page_count": 418, "format": Format.HARDCOVER},  # Overlap book
]

SAMPLE_REVIEWS = [
    "A profound meditation on memory and regret. Ishiguro's prose is masterful.",
    "This book completely changed my perspective. The narrative structure is innovative and compelling.",
    "Beautifully written but emotionally devastating. I couldn't put it down.",
    "A slow burn that rewards patience. The character development is exceptional.",
    "One of the best books I've read this year. The themes are timeless and relevant.",
    "The writing is lyrical and the story is haunting. Highly recommend.",
    "A masterpiece of speculative fiction. Thought-provoking and beautifully crafted.",
    "I found this book deeply moving. The author's voice is unique and powerful.",
    "An incredible journey. The world-building is immersive and detailed.",
    "This book made me think about things in a completely new way. Brilliant.",
    "The prose is stunning and the characters are unforgettable.",
    "A powerful exploration of identity and belonging. Truly remarkable.",
    "I was completely absorbed from start to finish. Exceptional storytelling.",
    "The themes are complex but accessible. A truly great work of literature.",
    "This book has stayed with me long after finishing. Highly impactful.",
]

def get_random_date_in_range(start_date: date, end_date: date) -> date:
    """Get a random date between start and end"""
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)

def calculate_points_for_read(book: Book, is_reread: bool = False) -> tuple:
    """Calculate points for a read"""
    points_allegory, points_reasonable = PointCalculator.calculate_points(
        book_type=book.book_type,
        page_count=book.page_count,
        is_reread=is_reread
    )
    return points_allegory, points_reasonable

def create_dummy_data():
    db = SessionLocal()
    
    try:
        # Find or create kagua user
        kagua = db.query(User).filter(User.username == "kagua").first()
        if not kagua:
            kagua = User(
                username="kagua",
                email="kagua@example.com",
                password_hash=get_password_hash("password123"),
                display_name="Kagua",
                is_active=True
            )
            db.add(kagua)
            db.commit()
            db.refresh(kagua)
            print(f"Created user: kagua (ID: {kagua.id})")
        else:
            print(f"Found user: kagua (ID: {kagua.id})")
        
        # Find kakaner user and get 3 of their books to overlap
        kakaner = db.query(User).filter(User.username == "kakaner").first()
        overlap_books = []
        if kakaner:
            kakaner_books = db.query(Book).filter(Book.user_id == kakaner.id).limit(10).all()
            if len(kakaner_books) >= 3:
                overlap_books = random.sample(kakaner_books, 3)
                print(f"Found {len(overlap_books)} books from kakaner to overlap")
            else:
                print(f"Kakaner only has {len(kakaner_books)} books, will create overlap books manually")
        else:
            print("Kakaner user not found, will create overlap books manually")
        
        # Create books
        books_to_create = 75
        formats = list(Format)
        book_types = list(BookType)
        genres_list = [
            ["literary fiction"], ["science fiction"], ["fantasy"], ["mystery"], ["thriller"],
            ["historical fiction"], ["contemporary fiction"], ["magical realism"], ["horror"],
            ["romance"], ["dystopian"], ["coming of age"], ["family saga"], ["psychological fiction"]
        ]
        
        created_books = []
        overlap_count = 0
        
        # Date range: past 10 years
        end_date = date.today()
        start_date = date(end_date.year - 10, 1, 1)
        
        for i in range(books_to_create):
            # Check if we need to create overlap books
            if overlap_count < 3 and overlap_books:
                # Use one of kakaner's books
                kakaner_book = overlap_books[overlap_count]
                book_data = {
                    "title": kakaner_book.title,
                    "author": kakaner_book.author,
                    "book_type": kakaner_book.book_type,
                    "page_count": kakaner_book.page_count,
                    "format": random.choice(formats),
                    "publication_date": kakaner_book.publication_date,
                    "publisher": kakaner_book.publisher,
                    "language": kakaner_book.language or "en",
                    "genres": kakaner_book.genres or random.choice(genres_list),
                    "description": kakaner_book.description,
                    "description_source": kakaner_book.description_source
                }
                overlap_count += 1
                print(f"Creating overlap book: {book_data['title']}")
            else:
                # Use sample book data
                sample = random.choice(SAMPLE_BOOKS)
                book_data = {
                    "title": sample["title"],
                    "author": sample["author"],
                    "book_type": sample["book_type"],
                    "page_count": sample["page_count"],
                    "format": sample["format"],
                    "publication_date": date(random.randint(1950, 2020), random.randint(1, 12), random.randint(1, 28)),
                    "publisher": f"Publisher {random.randint(1, 20)}",
                    "language": "en",
                    "genres": random.choice(genres_list),
                    "description": f"A compelling story about {sample['title']}.",
                    "description_source": DescriptionSource.MANUAL
                }
            
            # Create book
            book = Book(
                user_id=kagua.id,
                title=book_data["title"],
                author=book_data["author"],
                book_type=book_data["book_type"],
                page_count=book_data["page_count"],
                format=book_data["format"],
                publication_date=book_data.get("publication_date"),
                publisher=book_data.get("publisher"),
                language=book_data.get("language", "en"),
                genres=book_data.get("genres"),
                description=book_data.get("description"),
                description_source=book_data.get("description_source")
            )
            db.add(book)
            db.flush()  # Get the book ID
            
            # Determine number of reads for this book (most have 1, some have 2-3)
            num_reads = 1
            if random.random() < 0.15:  # 15% chance of 2 reads
                num_reads = 2
            elif random.random() < 0.05:  # 5% chance of 3 reads
                num_reads = 3
            
            # Create reads
            for read_num in range(num_reads):
                is_reread = read_num > 0
                
                # Random date in the past 10 years
                read_date = get_random_date_in_range(start_date, end_date)
                
                # Calculate points
                points_allegory, points_reasonable = calculate_points_for_read(book, is_reread)
                
                # 30% chance of having a review
                review = None
                if random.random() < 0.3:
                    review = random.choice(SAMPLE_REVIEWS)
                
                read = Read(
                    book_id=book.id,
                    user_id=kagua.id,
                    date_started=read_date - timedelta(days=random.randint(5, 30)),
                    date_finished=read_date,
                    read_status=ReadStatus.READ,
                    is_reread=is_reread,
                    review=review,
                    calculated_points_allegory=points_allegory,
                    calculated_points_reasonable=points_reasonable
                )
                db.add(read)
            
            created_books.append(book)
            
            if (i + 1) % 10 == 0:
                print(f"Created {i + 1} books...")
        
        db.commit()
        print(f"\nSuccessfully created {len(created_books)} books for kagua!")
        print(f"Created {overlap_count} overlap books with kakaner")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating dummy data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating dummy library data for user 'kagua'...")
    create_dummy_data()

