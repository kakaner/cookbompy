"""remove_semester_number_from_books

Revision ID: 3a3c2d7f28c1
Revises: 676580201017
Create Date: 2025-12-07 16:26:19.385649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a3c2d7f28c1'
down_revision = '676580201017'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove semester_number column from books table
    # Books will now be queried by date_finished range instead
    op.drop_index('ix_books_semester_number', 'books', if_exists=True)
    op.drop_column('books', 'semester_number')


def downgrade() -> None:
    # Re-add semester_number column (nullable, will need to be backfilled)
    op.add_column('books', sa.Column('semester_number', sa.Integer(), nullable=True))
    op.create_index('ix_books_semester_number', 'books', ['semester_number'])

