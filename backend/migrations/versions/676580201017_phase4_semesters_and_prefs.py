"""phase4_semesters_and_prefs

Revision ID: 676580201017
Revises: 0e116f853ef4
Create Date: 2025-12-07 11:26:18.424216

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '676580201017'
down_revision = '0e116f853ef4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create semesters table
    op.create_table(
        'semesters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('semester_number', sa.Integer(), nullable=False),
        sa.Column('custom_name', sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.UniqueConstraint('user_id', 'semester_number', name='uq_user_semester')
    )
    op.create_index('ix_semesters_id', 'semesters', ['id'])
    op.create_index('ix_semesters_user_id', 'semesters', ['user_id'])
    op.create_index('ix_semesters_semester_number', 'semesters', ['semester_number'])
    
    # Add semester_number to books
    op.add_column('books', sa.Column('semester_number', sa.Integer(), nullable=True))
    op.create_index('ix_books_semester_number', 'books', ['semester_number'])
    
    # Add user preference columns
    op.add_column('users', sa.Column('profile_photo_url', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('default_book_format', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('color_theme', sa.String(50), nullable=True, server_default='terracotta'))
    op.add_column('users', sa.Column('default_page_size', sa.Integer(), nullable=True, server_default='50'))


def downgrade() -> None:
    # Remove user preference columns
    op.drop_column('users', 'default_page_size')
    op.drop_column('users', 'color_theme')
    op.drop_column('users', 'default_book_format')
    op.drop_column('users', 'profile_photo_url')
    
    # Remove semester_number from books
    op.drop_index('ix_books_semester_number', 'books')
    op.drop_column('books', 'semester_number')
    
    # Drop semesters table
    op.drop_index('ix_semesters_semester_number', 'semesters')
    op.drop_index('ix_semesters_user_id', 'semesters')
    op.drop_index('ix_semesters_id', 'semesters')
    op.drop_table('semesters')

