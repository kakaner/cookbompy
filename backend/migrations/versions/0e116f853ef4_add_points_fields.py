"""add_points_fields

Revision ID: 0e116f853ef4
Revises: 09e0d169ee64
Create Date: 2025-12-07 10:58:56.064628

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e116f853ef4'
down_revision = '09e0d169ee64'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add point system fields to books table
    op.add_column('books', sa.Column('base_points', sa.Integer(), nullable=True))
    op.add_column('books', sa.Column('base_points_overridden', sa.Boolean(), nullable=True, server_default='0'))
    op.add_column('books', sa.Column('calculated_points_allegory', sa.Integer(), nullable=True))
    op.add_column('books', sa.Column('calculated_points_reasonable', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove point system fields
    op.drop_column('books', 'calculated_points_reasonable')
    op.drop_column('books', 'calculated_points_allegory')
    op.drop_column('books', 'base_points_overridden')
    op.drop_column('books', 'base_points')

