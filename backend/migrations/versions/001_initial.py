"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=72), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True),
        sa.Column('email_notifications_enabled', sa.Boolean(), nullable=True),
        sa.Column('email_on_comment', sa.Boolean(), nullable=True),
        sa.Column('email_on_mention', sa.Boolean(), nullable=True),
        sa.Column('oauth_provider', sa.String(length=50), nullable=True),
        sa.Column('oauth_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Genres table
    op.create_table(
        'genres',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_genres_id'), 'genres', ['id'], unique=False)
    op.create_index(op.f('ix_genres_name'), 'genres', ['name'], unique=True)

    # Tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tags_id'), 'tags', ['id'], unique=False)
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=True)

    # Books table
    op.create_table(
        'books',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('isbn', sa.String(length=20), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('author', sa.String(length=500), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('cover_image_url', sa.String(length=500), nullable=True),
        sa.Column('published_year', sa.Integer(), nullable=True),
        sa.Column('publisher', sa.String(length=255), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_books_author'), 'books', ['author'], unique=False)
    op.create_index(op.f('ix_books_id'), 'books', ['id'], unique=False)
    op.create_index(op.f('ix_books_isbn'), 'books', ['isbn'], unique=True)
    op.create_index(op.f('ix_books_title'), 'books', ['title'], unique=False)

    # Book-Genre association
    op.create_table(
        'book_genres',
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('genre_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
        sa.ForeignKeyConstraint(['genre_id'], ['genres.id'], ),
        sa.PrimaryKeyConstraint('book_id', 'genre_id')
    )

    # Book-Tag association
    op.create_table(
        'book_tags',
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
        sa.PrimaryKeyConstraint('book_id', 'tag_id')
    )

    # User Books table
    op.create_table(
        'user_books',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('TO_READ', 'READING', 'COMPLETED', 'ABANDONED', name='readingstatus'), nullable=True),
        sa.Column('date_started', sa.DateTime(), nullable=True),
        sa.Column('date_finished', sa.DateTime(), nullable=True),
        sa.Column('date_abandoned', sa.DateTime(), nullable=True),
        sa.Column('rating', sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column('would_recommend', sa.Enum('YES', 'NO', 'MAYBE', name='recommendationstatus'), nullable=True),
        sa.Column('recommendation_notes', sa.Text(), nullable=True),
        sa.Column('ownership_status', sa.Enum('OWNED_PHYSICAL', 'OWNED_KINDLE', 'OWNED_OTHER', 'BORROWED_FRIEND', 'BORROWED_LIBRARY', 'READ_BOOKSTORE', 'OTHER', name='ownershipstatus'), nullable=True),
        sa.Column('user_summary', sa.Text(), nullable=True),
        sa.Column('review', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_books_book_id'), 'user_books', ['book_id'], unique=False)
    op.create_index(op.f('ix_user_books_id'), 'user_books', ['id'], unique=False)
    op.create_index(op.f('ix_user_books_status'), 'user_books', ['status'], unique=False)
    op.create_index(op.f('ix_user_books_user_id'), 'user_books', ['user_id'], unique=False)

    # Reading Locations table
    op.create_table(
        'reading_locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_book_id', sa.Integer(), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(['user_book_id'], ['user_books.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reading_locations_id'), 'reading_locations', ['id'], unique=False)
    op.create_index(op.f('ix_reading_locations_user_book_id'), 'reading_locations', ['user_book_id'], unique=False)

    # Comments table
    op.create_table(
        'user_book_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('user_book_id', sa.Integer(), nullable=False),
        sa.Column('parent_comment_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['parent_comment_id'], ['user_book_comments.id'], ),
        sa.ForeignKeyConstraint(['user_book_id'], ['user_books.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_book_comments_id'), 'user_book_comments', ['id'], unique=False)
    op.create_index(op.f('ix_user_book_comments_user_book_id'), 'user_book_comments', ['user_book_id'], unique=False)
    op.create_index(op.f('ix_user_book_comments_user_id'), 'user_book_comments', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_book_comments_user_id'), table_name='user_book_comments')
    op.drop_index(op.f('ix_user_book_comments_user_book_id'), table_name='user_book_comments')
    op.drop_index(op.f('ix_user_book_comments_id'), table_name='user_book_comments')
    op.drop_table('user_book_comments')
    op.drop_index(op.f('ix_reading_locations_user_book_id'), table_name='reading_locations')
    op.drop_index(op.f('ix_reading_locations_id'), table_name='reading_locations')
    op.drop_table('reading_locations')
    op.drop_index(op.f('ix_user_books_user_id'), table_name='user_books')
    op.drop_index(op.f('ix_user_books_status'), table_name='user_books')
    op.drop_index(op.f('ix_user_books_id'), table_name='user_books')
    op.drop_index(op.f('ix_user_books_book_id'), table_name='user_books')
    op.drop_table('user_books')
    op.drop_table('book_tags')
    op.drop_table('book_genres')
    op.drop_index(op.f('ix_books_title'), table_name='books')
    op.drop_index(op.f('ix_books_isbn'), table_name='books')
    op.drop_index(op.f('ix_books_id'), table_name='books')
    op.drop_index(op.f('ix_books_author'), table_name='books')
    op.drop_table('books')
    op.drop_index(op.f('ix_tags_name'), table_name='tags')
    op.drop_index(op.f('ix_tags_id'), table_name='tags')
    op.drop_table('tags')
    op.drop_index(op.f('ix_genres_name'), table_name='genres')
    op.drop_index(op.f('ix_genres_id'), table_name='genres')
    op.drop_table('genres')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

