from enum import Enum


class Format(str, Enum):
    """Book format types"""
    HARDCOVER = "HARDCOVER"
    PAPERBACK = "PAPERBACK"
    MASS_MARKET_PAPERBACK = "MASS_MARKET_PAPERBACK"
    TRADE_PAPERBACK = "TRADE_PAPERBACK"
    LEATHER_BOUND = "LEATHER_BOUND"
    KINDLE = "KINDLE"
    PDF = "PDF"
    EPUB = "EPUB"
    OTHER_DIGITAL = "OTHER_DIGITAL"
    AUDIOBOOK_AUDIBLE = "AUDIOBOOK_AUDIBLE"
    AUDIOBOOK_OTHER = "AUDIOBOOK_OTHER"
    AUDIOBOOK_CD = "AUDIOBOOK_CD"
    ANTHOLOGY = "ANTHOLOGY"
    MAGAZINE = "MAGAZINE"
    OTHER = "OTHER"


class BookType(str, Enum):
    """Book type/category"""
    FICTION = "FICTION"
    NONFICTION = "NONFICTION"
    YA = "YA"
    CHILDRENS = "CHILDRENS"
    COMIC = "COMIC"
    NOVELLA = "NOVELLA"
    SHORT_STORY = "SHORT_STORY"
    OTHER = "OTHER"


class ReadStatus(str, Enum):
    """Reading status"""
    UNREAD = "UNREAD"
    READING = "READING"
    READ = "READ"
    DNF = "DNF"  # Did Not Finish


class DescriptionSource(str, Enum):
    """Source of book description/synopsis"""
    GOODREADS = "GOODREADS"
    GOOGLE_BOOKS = "GOOGLE_BOOKS"
    AMAZON = "AMAZON"
    WIKIPEDIA = "WIKIPEDIA"
    MANUAL = "MANUAL"

