"""add_shareable_links

Revision ID: 75872fb16116
Revises: be26a137e326
Create Date: 2025-12-08 12:31:08.203314

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75872fb16116'
down_revision = 'be26a137e326'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'shareable_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shareable_links_id'), 'shareable_links', ['id'], unique=False)
    op.create_index(op.f('ix_shareable_links_book_id'), 'shareable_links', ['book_id'], unique=False)
    op.create_index(op.f('ix_shareable_links_token'), 'shareable_links', ['token'], unique=True)
    op.create_index(op.f('ix_shareable_links_expires_at'), 'shareable_links', ['expires_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_shareable_links_expires_at'), table_name='shareable_links')
    op.drop_index(op.f('ix_shareable_links_token'), table_name='shareable_links')
    op.drop_index(op.f('ix_shareable_links_book_id'), table_name='shareable_links')
    op.drop_index(op.f('ix_shareable_links_id'), table_name='shareable_links')
    op.drop_table('shareable_links')

