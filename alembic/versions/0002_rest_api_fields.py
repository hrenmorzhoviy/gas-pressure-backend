"""Add REST API system fields and user password.

Revision ID: 0002
Revises: 0001
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(255), nullable=False, server_default="change-me"))
    op.add_column("gases", sa.Column("creator_id", sa.Integer(), nullable=True))
    op.add_column("gases", sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.add_column("gases", sa.Column("published_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key("fk_gases_creator", "gases", "users", ["creator_id"], ["id"])
    op.execute("UPDATE gases SET creator_id = 1 WHERE creator_id IS NULL")
    op.alter_column("gases", "creator_id", nullable=False)
    op.alter_column("gases", "description", nullable=True)
    op.alter_column("gases", "molar_mass", nullable=True)
    op.alter_column("gases", "density", nullable=True)


def downgrade() -> None:
    op.alter_column("gases", "density", nullable=False)
    op.alter_column("gases", "molar_mass", nullable=False)
    op.alter_column("gases", "description", nullable=False)
    op.drop_constraint("fk_gases_creator", "gases", type_="foreignkey")
    op.drop_column("gases", "published_at")
    op.drop_column("gases", "created_at")
    op.drop_column("gases", "creator_id")
    op.drop_column("users", "password_hash")
