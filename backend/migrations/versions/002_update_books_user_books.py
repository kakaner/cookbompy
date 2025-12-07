"""Update books ISBN constraint and add user book fields

Revision ID: 002_update_books_user_books
Revises: 001_initial
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_update_books_user_books'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "sqlite":
        # SQLite requires table rebuild to drop UNIQUE constraint
        op.create_table(
            "books_tmp",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("isbn", sa.String(length=20), nullable=True),
            sa.Column("title", sa.String(length=500), nullable=False, index=True),
            sa.Column("author", sa.String(length=500), nullable=True, index=True),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("cover_image_url", sa.String(length=500), nullable=True),
            sa.Column("published_year", sa.Integer(), nullable=True),
            sa.Column("publisher", sa.String(length=255), nullable=True),
            sa.Column("page_count", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )

        bind.execute(sa.text(
            "INSERT INTO books_tmp (id, isbn, title, author, summary, cover_image_url, published_year, publisher, page_count, created_at, updated_at) "
            "SELECT id, isbn, title, author, summary, cover_image_url, published_year, publisher, page_count, created_at, updated_at FROM books"
        ))

        op.drop_table("books")
        op.rename_table("books_tmp", "books")
        op.create_index("ix_books_id", "books", ["id"], unique=False)
        op.create_index("ix_books_isbn", "books", ["isbn"], unique=False)
        op.create_index("ix_books_title", "books", ["title"], unique=False)
        op.create_index("ix_books_author", "books", ["author"], unique=False)
    else:
        inspector = sa.inspect(bind)
        unique_constraints = {uc['name'] for uc in inspector.get_unique_constraints('books') if uc.get('name')}

        if unique_constraints:
            possible_names = unique_constraints | {'books_isbn_key', 'uq_books_isbn'}
            for name in possible_names:
                with op.batch_alter_table('books') as batch_op:
                    try:
                        batch_op.drop_constraint(name, type_='unique')
                        break
                    except ValueError:
                        continue

    # Add new columns to user_books
    with op.batch_alter_table('user_books') as batch_op:
        batch_op.add_column(sa.Column('book_review', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('date_added_to_platform', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
        batch_op.add_column(sa.Column('date_read', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('date_acquired', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('user_books') as batch_op:
        batch_op.drop_column('date_acquired')
        batch_op.drop_column('date_read')
        batch_op.drop_column('date_added_to_platform')
        batch_op.drop_column('book_review')

    with op.batch_alter_table('books') as batch_op:
        batch_op.create_unique_constraint('books_isbn_key', ['isbn'])

