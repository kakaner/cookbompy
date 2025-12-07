"""phase2_books

Revision ID: 09e0d169ee64
Revises: 006_phase1
Create Date: 2025-12-07 09:53:03.298939

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09e0d169ee64'
down_revision = '006_phase1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create books table
    op.create_table(
        'books',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('author', sa.String(length=500), nullable=False),
        sa.Column('isbn_10', sa.String(length=13), nullable=True),
        sa.Column('isbn_13', sa.String(length=17), nullable=True),
        sa.Column('publication_date', sa.Date(), nullable=True),
        sa.Column('publisher', sa.String(length=255), nullable=True),
        sa.Column('edition', sa.String(length=100), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('language', sa.String(length=50), nullable=True),
        sa.Column('cover_image_url', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('description_source', sa.Enum('GOODREADS', 'GOOGLE_BOOKS', 'AMAZON', 'WIKIPEDIA', 'MANUAL', name='descriptionsource'), nullable=True),
        sa.Column('genres', sa.JSON(), nullable=True),
        sa.Column('book_type', sa.Enum('FICTION', 'NONFICTION', 'YA', 'CHILDRENS', 'COMIC', 'NOVELLA', 'SHORT_STORY', 'OTHER', name='booktype'), nullable=True),
        sa.Column('series', sa.String(length=255), nullable=True),
        sa.Column('series_number', sa.Integer(), nullable=True),
        sa.Column('original_title', sa.String(length=500), nullable=True),
        sa.Column('translator', sa.String(length=255), nullable=True),
        sa.Column('illustrator', sa.String(length=255), nullable=True),
        sa.Column('awards', sa.Text(), nullable=True),
        sa.Column('acquisition_date', sa.Date(), nullable=True),
        sa.Column('acquisition_source', sa.String(length=255), nullable=True),
        sa.Column('physical_location', sa.String(length=255), nullable=True),
        sa.Column('condition_notes', sa.Text(), nullable=True),
        sa.Column('lending_status', sa.String(length=255), nullable=True),
        sa.Column('read_vibe_photo_url', sa.String(length=500), nullable=True),
        sa.Column('date_started', sa.Date(), nullable=True),
        sa.Column('date_finished', sa.Date(), nullable=True),
        sa.Column('is_reread', sa.Boolean(), nullable=True),
        sa.Column('read_status', sa.Enum('UNREAD', 'READING', 'READ', 'DNF', name='readstatus'), nullable=True),
        sa.Column('format', sa.Enum('HARDCOVER', 'PAPERBACK', 'MASS_MARKET_PAPERBACK', 'TRADE_PAPERBACK', 'LEATHER_BOUND', 'KINDLE', 'PDF', 'EPUB', 'OTHER_DIGITAL', 'AUDIOBOOK_AUDIBLE', 'AUDIOBOOK_OTHER', 'AUDIOBOOK_CD', 'ANTHOLOGY', 'MAGAZINE', 'OTHER', name='format'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_books_id'), 'books', ['id'], unique=False)
    op.create_index(op.f('ix_books_user_id'), 'books', ['user_id'], unique=False)
    op.create_index(op.f('ix_books_title'), 'books', ['title'], unique=False)
    op.create_index(op.f('ix_books_author'), 'books', ['author'], unique=False)
    op.create_index(op.f('ix_books_isbn_13'), 'books', ['isbn_13'], unique=False)
    op.create_index(op.f('ix_books_format'), 'books', ['format'], unique=False)
    op.create_index(op.f('ix_books_book_type'), 'books', ['book_type'], unique=False)
    op.create_index(op.f('ix_books_read_status'), 'books', ['read_status'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_books_read_status'), table_name='books')
    op.drop_index(op.f('ix_books_book_type'), table_name='books')
    op.drop_index(op.f('ix_books_format'), table_name='books')
    op.drop_index(op.f('ix_books_isbn_13'), table_name='books')
    op.drop_index(op.f('ix_books_author'), table_name='books')
    op.drop_index(op.f('ix_books_title'), table_name='books')
    op.drop_index(op.f('ix_books_user_id'), table_name='books')
    op.drop_index(op.f('ix_books_id'), table_name='books')
    
    # Drop table
    op.drop_table('books')
    
    # Drop enums
    sa.Enum(name='readstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='format').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='booktype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='descriptionsource').drop(op.get_bind(), checkfirst=True)

