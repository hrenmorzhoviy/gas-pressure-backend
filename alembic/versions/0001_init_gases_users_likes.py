"""init gases, users and likes tables

Revision ID: 0001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Таблица пользователей ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    # --- Таблица газов ---
    op.create_table(
        "gases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("molar_mass", sa.Float(), nullable=False),
        sa.Column("density", sa.Float(), nullable=False),
        sa.Column("description", sa.String(1000), nullable=False),
        sa.Column("image_key", sa.String(255), nullable=False, server_default=""),
        sa.Column("video_key", sa.String(255), nullable=False, server_default=""),
        sa.Column("image_url", sa.String(512), nullable=False, server_default=""),
        sa.Column("video_url", sa.String(512), nullable=False, server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("is_deleted", sa.Boolean(), nullable=True, server_default="false"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_gases_id"), "gases", ["id"], unique=False)

    # --- Таблица лайков (м-м) ---
    op.create_table(
        "likes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("gas_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["gas_id"], ["gases.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "gas_id", name="uq_user_gas_like"),
    )
    op.create_index(op.f("ix_likes_id"), "likes", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_likes_id"), table_name="likes")
    op.drop_table("likes")
    op.drop_index(op.f("ix_gases_id"), table_name="gases")
    op.drop_table("gases")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
