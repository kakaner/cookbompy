"""Add audible and Goodreads fields plus acquisition info

Revision ID: 003_book_library_enhancements
Revises: 002_update_books_user_books
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_book_library_enhancements'
down_revision = '002_update_books_user_books'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('books', sa.Column('goodreads_url', sa.String(length=500), nullable=True))
    op.add_column('books', sa.Column('is_audible', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column('user_books', sa.Column('acquired_from', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('user_books', 'acquired_from')
    op.drop_column('books', 'is_audible')
    op.drop_column('books', 'goodreads_url')

