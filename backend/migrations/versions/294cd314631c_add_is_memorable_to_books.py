"""add_is_memorable_to_books

Revision ID: 294cd314631c
Revises: 3a3c2d7f28c1
Create Date: 2025-12-07 16:31:43.972109

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '294cd314631c'
down_revision = '3a3c2d7f28c1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_memorable column to books table
    op.add_column('books', sa.Column('is_memorable', sa.Boolean(), nullable=False, server_default='0'))
    op.create_index('ix_books_is_memorable', 'books', ['is_memorable'])


def downgrade() -> None:
    # Remove is_memorable column
    op.drop_index('ix_books_is_memorable', 'books')
    op.drop_column('books', 'is_memorable')

