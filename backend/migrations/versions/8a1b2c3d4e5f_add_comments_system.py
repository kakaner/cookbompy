"""add_comments_system

Revision ID: 8a1b2c3d4e5f
Revises: 7ddeebb442b4
Create Date: 2025-12-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a1b2c3d4e5f'
down_revision = '7ddeebb442b4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create comments table
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('read_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('parent_comment_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['read_id'], ['reads.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_comment_id'], ['comments.id'], ondelete='CASCADE')
    )
    op.create_index('ix_comments_id', 'comments', ['id'])
    op.create_index('ix_comments_read_id', 'comments', ['read_id'])
    op.create_index('ix_comments_user_id', 'comments', ['user_id'])
    op.create_index('ix_comments_parent_comment_id', 'comments', ['parent_comment_id'])
    op.create_index('ix_comments_created_at', 'comments', ['created_at'])
    
    # Create comment_reactions table
    op.create_table(
        'comment_reactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('comment_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('reaction_type', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('comment_id', 'user_id', 'reaction_type', name='uq_comment_reaction')
    )
    op.create_index('ix_comment_reactions_id', 'comment_reactions', ['id'])
    op.create_index('ix_comment_reactions_comment_id', 'comment_reactions', ['comment_id'])
    op.create_index('ix_comment_reactions_user_id', 'comment_reactions', ['user_id'])


def downgrade() -> None:
    # Drop comment_reactions table
    op.drop_index('ix_comment_reactions_user_id', 'comment_reactions')
    op.drop_index('ix_comment_reactions_comment_id', 'comment_reactions')
    op.drop_index('ix_comment_reactions_id', 'comment_reactions')
    op.drop_table('comment_reactions')
    
    # Drop comments table
    op.drop_index('ix_comments_created_at', 'comments')
    op.drop_index('ix_comments_parent_comment_id', 'comments')
    op.drop_index('ix_comments_user_id', 'comments')
    op.drop_index('ix_comments_read_id', 'comments')
    op.drop_index('ix_comments_id', 'comments')
    op.drop_table('comments')

