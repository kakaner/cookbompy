"""add_rating_to_reads

Revision ID: da4371b8638c
Revises: 8a1b2c3d4e5f
Create Date: 2025-12-08 09:06:53.908458

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da4371b8638c'
down_revision = '8a1b2c3d4e5f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add rating column to reads table
    # Rating: Float, nullable, 0.5 to 10.0 in 0.5 increments
    op.add_column('reads', sa.Column('rating', sa.Float(), nullable=True))
    # Add index for rating queries
    op.create_index(op.f('ix_reads_rating'), 'reads', ['rating'], unique=False)


def downgrade() -> None:
    # Remove rating column and index
    op.drop_index(op.f('ix_reads_rating'), table_name='reads')
    op.drop_column('reads', 'rating')

