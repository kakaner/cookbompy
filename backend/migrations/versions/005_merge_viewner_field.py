"""Merge review fields into viewner

Revision ID: 005_merge_viewner_field
Revises: 004_book_language_points
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "005_merge_viewner_field"
down_revision = "004_book_language_points"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("user_books") as batch_op:
        batch_op.add_column(sa.Column("viewner", sa.Text(), nullable=True))

    bind = op.get_bind()
    user_books = bind.execute(
        sa.text("SELECT id, review, book_review FROM user_books")
    ).fetchall()

    for row in user_books:
        content = row.review or row.book_review
        if content:
            bind.execute(
                sa.text("UPDATE user_books SET viewner = :content WHERE id = :id"),
                {"content": content, "id": row.id},
            )

    with op.batch_alter_table("user_books") as batch_op:
        batch_op.drop_column("review")
        batch_op.drop_column("book_review")


def downgrade() -> None:
    with op.batch_alter_table("user_books") as batch_op:
        batch_op.add_column(sa.Column("review", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("book_review", sa.Text(), nullable=True))

    bind = op.get_bind()
    user_books = bind.execute(
        sa.text("SELECT id, viewner FROM user_books")
    ).fetchall()

    for row in user_books:
        if row.viewner:
            bind.execute(
                sa.text("UPDATE user_books SET review = :content WHERE id = :id"),
                {"content": row.viewner, "id": row.id},
            )

    with op.batch_alter_table("user_books") as batch_op:
        batch_op.drop_column("viewner")

