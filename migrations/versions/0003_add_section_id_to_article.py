"""add section_id to article

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("article", sa.Column("section_id", sa.Uuid(), nullable=True))
    op.create_index("ix_article_section_id", "article", ["section_id"])
    op.create_foreign_key(
        "article_section_id_fkey",
        "article",
        "section",
        ["section_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("article_section_id_fkey", "article", type_="foreignkey")
    op.drop_index("ix_article_section_id", table_name="article")
    op.drop_column("article", "section_id")
