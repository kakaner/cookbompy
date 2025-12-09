"""add_default_home_page_preference

Revision ID: 119210c8e4e3
Revises: da4371b8638c
Create Date: 2025-12-08 09:20:18.747421

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '119210c8e4e3'
down_revision = 'da4371b8638c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add default_home_page column to users table
    op.add_column('users', sa.Column('default_home_page', sa.String(50), nullable=True, server_default='library'))


def downgrade() -> None:
    # Remove default_home_page column
    op.drop_column('users', 'default_home_page')

