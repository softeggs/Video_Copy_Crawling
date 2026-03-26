"""create users and videos

Revision ID: 20260320_0001
Revises:
Create Date: 2026-03-20 17:35:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260320_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("table_id", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "videos",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("author", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("core_points", sa.JSON(), nullable=False),
        sa.Column("corrected_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("golden_sentences", sa.JSON(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("video_type", sa.String(length=255), nullable=False, server_default="其他"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="待处理"),
        sa.Column("markdown_content", sa.Text(), nullable=False, server_default=""),
        sa.Column("error_msg", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_videos_user_id", "videos", ["user_id"], unique=False)
    op.create_index("ix_videos_status", "videos", ["status"], unique=False)
    op.create_index("ix_videos_created_at", "videos", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_videos_created_at", table_name="videos")
    op.drop_index("ix_videos_status", table_name="videos")
    op.drop_index("ix_videos_user_id", table_name="videos")
    op.drop_table("videos")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
