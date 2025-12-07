"""Add language, book_type, points, is_reread columns

Revision ID: 004_book_language_points
Revises: 003_book_library_enhancements
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_book_language_points'
down_revision = '003_book_library_enhancements'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('books') as batch_op:
        batch_op.add_column(sa.Column('language', sa.String(length=8), nullable=True))
        batch_op.add_column(sa.Column('book_type', sa.String(length=50), nullable=True))

    with op.batch_alter_table('user_books') as batch_op:
        batch_op.add_column(sa.Column('is_reread', sa.Boolean(), server_default=sa.false(), nullable=False))
        batch_op.add_column(sa.Column('points', sa.Float(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('user_books') as batch_op:
        batch_op.drop_column('points')
        batch_op.drop_column('is_reread')

    with op.batch_alter_table('books') as batch_op:
        batch_op.drop_column('book_type')
        batch_op.drop_column('language')

