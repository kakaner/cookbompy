"""add_semester_comments

Revision ID: be26a137e326
Revises: 119210c8e4e3
Create Date: 2025-12-08 12:15:31.719893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'be26a137e326'
down_revision = '119210c8e4e3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
    # Step 1: Create new table with nullable read_id and semester_id
    op.create_table(
        'comments_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('read_id', sa.Integer(), nullable=True),
        sa.Column('semester_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('parent_comment_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['read_id'], ['reads.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['semester_id'], ['semesters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_comment_id'], ['comments_new.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_new_id'), 'comments_new', ['id'], unique=False)
    op.create_index(op.f('ix_comments_new_read_id'), 'comments_new', ['read_id'], unique=False)
    op.create_index(op.f('ix_comments_new_semester_id'), 'comments_new', ['semester_id'], unique=False)
    op.create_index(op.f('ix_comments_new_user_id'), 'comments_new', ['user_id'], unique=False)
    op.create_index(op.f('ix_comments_new_parent_comment_id'), 'comments_new', ['parent_comment_id'], unique=False)
    
    # Step 2: Copy data from old table to new table
    op.execute("""
        INSERT INTO comments_new (id, read_id, user_id, parent_comment_id, content, is_deleted, deleted_at, created_at, updated_at)
        SELECT id, read_id, user_id, parent_comment_id, content, is_deleted, deleted_at, created_at, updated_at
        FROM comments
    """)
    
    # Step 3: Copy comment_reactions (they reference comments by id, so they should still work)
    # But we need to update the foreign key constraint
    
    # Step 4: Drop old table and rename new table
    op.drop_table('comments')
    op.rename_table('comments_new', 'comments')
    
    # Step 5: Recreate indexes with correct names
    op.create_index('ix_comments_id', 'comments', ['id'], unique=False)
    op.create_index('ix_comments_read_id', 'comments', ['read_id'], unique=False)
    op.create_index('ix_comments_semester_id', 'comments', ['semester_id'], unique=False)
    op.create_index('ix_comments_user_id', 'comments', ['user_id'], unique=False)
    op.create_index('ix_comments_parent_comment_id', 'comments', ['parent_comment_id'], unique=False)


def downgrade() -> None:
    # Reverse the process - recreate table with non-nullable read_id
    op.create_table(
        'comments_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('read_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('parent_comment_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['read_id'], ['reads.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_comment_id'], ['comments_new.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Copy only comments with read_id (drop semester comments)
    op.execute("""
        INSERT INTO comments_new (id, read_id, user_id, parent_comment_id, content, is_deleted, deleted_at, created_at, updated_at)
        SELECT id, read_id, user_id, parent_comment_id, content, is_deleted, deleted_at, created_at, updated_at
        FROM comments
        WHERE read_id IS NOT NULL
    """)
    
    op.drop_table('comments')
    op.rename_table('comments_new', 'comments')
    
    op.create_index('ix_comments_id', 'comments', ['id'], unique=False)
    op.create_index('ix_comments_read_id', 'comments', ['read_id'], unique=False)
    op.create_index('ix_comments_user_id', 'comments', ['user_id'], unique=False)
    op.create_index('ix_comments_parent_comment_id', 'comments', ['parent_comment_id'], unique=False)

