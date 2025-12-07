"""add_reads_model_multiple_reads_per_book

Revision ID: 7ddeebb442b4
Revises: 294cd314631c
Create Date: 2025-12-07 16:39:13.562098

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ddeebb442b4'
down_revision = '294cd314631c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create reads table
    op.create_table(
        'reads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date_started', sa.Date(), nullable=True),
        sa.Column('date_finished', sa.Date(), nullable=True),
        sa.Column('read_status', sa.String(50), nullable=False, server_default='UNREAD'),
        sa.Column('is_reread', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('review', sa.Text(), nullable=True),
        sa.Column('read_vibe_photo_url', sa.String(500), nullable=True),
        sa.Column('base_points', sa.Integer(), nullable=True),
        sa.Column('base_points_overridden', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('calculated_points_allegory', sa.Integer(), nullable=True),
        sa.Column('calculated_points_reasonable', sa.Integer(), nullable=True),
        sa.Column('is_memorable', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['book_id'], ['books.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index('ix_reads_id', 'reads', ['id'])
    op.create_index('ix_reads_book_id', 'reads', ['book_id'])
    op.create_index('ix_reads_user_id', 'reads', ['user_id'])
    op.create_index('ix_reads_date_finished', 'reads', ['date_finished'])
    op.create_index('ix_reads_read_status', 'reads', ['read_status'])
    op.create_index('ix_reads_is_memorable', 'reads', ['is_memorable'])
    
    # Migrate existing book reading data to reads table
    # This creates a read for each book that has reading data
    op.execute("""
        INSERT INTO reads (book_id, user_id, date_started, date_finished, read_status, is_reread, 
                          read_vibe_photo_url, base_points, base_points_overridden, 
                          calculated_points_allegory, calculated_points_reasonable, is_memorable, created_at)
        SELECT id, user_id, date_started, date_finished, 
               CASE 
                   WHEN read_status = 'UNREAD' THEN 'UNREAD'
                   WHEN read_status = 'READING' THEN 'READING'
                   WHEN read_status = 'READ' THEN 'READ'
                   WHEN read_status = 'DNF' THEN 'DNF'
                   ELSE 'UNREAD'
               END,
               is_reread, read_vibe_photo_url, base_points, base_points_overridden,
               calculated_points_allegory, calculated_points_reasonable, is_memorable, created_at
        FROM books
        WHERE date_finished IS NOT NULL OR date_started IS NOT NULL OR read_status != 'UNREAD'
    """)
    
    # Remove reading-related columns from books table
    op.drop_index('ix_books_date_finished', 'books', if_exists=True)
    op.drop_index('ix_books_read_status', 'books', if_exists=True)
    op.drop_index('ix_books_is_memorable', 'books', if_exists=True)
    op.drop_column('books', 'date_started')
    op.drop_column('books', 'date_finished')
    op.drop_column('books', 'is_reread')
    op.drop_column('books', 'read_status')
    op.drop_column('books', 'read_vibe_photo_url')
    op.drop_column('books', 'base_points')
    op.drop_column('books', 'base_points_overridden')
    op.drop_column('books', 'calculated_points_allegory')
    op.drop_column('books', 'calculated_points_reasonable')
    op.drop_column('books', 'is_memorable')


def downgrade() -> None:
    # Re-add columns to books table
    op.add_column('books', sa.Column('date_started', sa.Date(), nullable=True))
    op.add_column('books', sa.Column('date_finished', sa.Date(), nullable=True))
    op.add_column('books', sa.Column('is_reread', sa.Boolean(), nullable=True))
    op.add_column('books', sa.Column('read_status', sa.String(50), nullable=True))
    op.add_column('books', sa.Column('read_vibe_photo_url', sa.String(500), nullable=True))
    op.add_column('books', sa.Column('base_points', sa.Integer(), nullable=True))
    op.add_column('books', sa.Column('base_points_overridden', sa.Boolean(), nullable=True))
    op.add_column('books', sa.Column('calculated_points_allegory', sa.Integer(), nullable=True))
    op.add_column('books', sa.Column('calculated_points_reasonable', sa.Integer(), nullable=True))
    op.add_column('books', sa.Column('is_memorable', sa.Boolean(), nullable=True))
    
    # Migrate data back (use the most recent read per book)
    op.execute("""
        UPDATE books
        SET date_started = (SELECT date_started FROM reads WHERE reads.book_id = books.id ORDER BY date_finished DESC LIMIT 1),
            date_finished = (SELECT date_finished FROM reads WHERE reads.book_id = books.id ORDER BY date_finished DESC LIMIT 1),
            is_reread = (SELECT is_reread FROM reads WHERE reads.book_id = books.id ORDER BY date_finished DESC LIMIT 1),
            read_status = (SELECT read_status FROM reads WHERE reads.book_id = books.id ORDER BY date_finished DESC LIMIT 1),
            read_vibe_photo_url = (SELECT read_vibe_photo_url FROM reads WHERE reads.book_id = books.id ORDER BY date_finished DESC LIMIT 1),
            base_points = (SELECT base_points FROM reads WHERE reads.book_id = books.id ORDER BY date_finished DESC LIMIT 1),
            base_points_overridden = (SELECT base_points_overridden FROM reads WHERE reads.book_id = books.id ORDER BY date_finished DESC LIMIT 1),
            calculated_points_allegory = (SELECT calculated_points_allegory FROM reads WHERE reads.book_id = books.id ORDER BY date_finished DESC LIMIT 1),
            calculated_points_reasonable = (SELECT calculated_points_reasonable FROM reads WHERE reads.book_id = books.id ORDER BY date_finished DESC LIMIT 1),
            is_memorable = (SELECT is_memorable FROM reads WHERE reads.book_id = books.id ORDER BY date_finished DESC LIMIT 1)
        WHERE EXISTS (SELECT 1 FROM reads WHERE reads.book_id = books.id)
    """)
    
    op.create_index('ix_books_date_finished', 'books', ['date_finished'])
    op.create_index('ix_books_read_status', 'books', ['read_status'])
    op.create_index('ix_books_is_memorable', 'books', ['is_memorable'])
    
    # Drop reads table
    op.drop_index('ix_reads_is_memorable', 'reads')
    op.drop_index('ix_reads_read_status', 'reads')
    op.drop_index('ix_reads_date_finished', 'reads')
    op.drop_index('ix_reads_user_id', 'reads')
    op.drop_index('ix_reads_book_id', 'reads')
    op.drop_index('ix_reads_id', 'reads')
    op.drop_table('reads')

