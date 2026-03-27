"""add favorites processing_stage shortcut_keys

Revision ID: 20260327_p3_new_fields
Revises: 20260320_0001
Create Date: 2026-03-27 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260327_p3_new_fields"
down_revision = "20260320_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # videos 表新增字段
    op.add_column("videos", sa.Column("is_favorited", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("videos", sa.Column("processing_stage", sa.String(length=32), nullable=False, server_default=""))
    op.add_column("videos", sa.Column("processing_detail", sa.Text(), nullable=False, server_default=""))
    op.add_column("videos", sa.Column("estimated_seconds_remaining", sa.Integer(), nullable=True))
    op.add_column("videos", sa.Column("last_stage_update_at", sa.DateTime(timezone=True), nullable=True))

    # shortcut_keys 表
    op.create_table(
        "shortcut_keys",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("key_hash", sa.String(length=512), nullable=False),
        sa.Column("key_prefix", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_shortcut_keys_user_id", "shortcut_keys", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_shortcut_keys_user_id", table_name="shortcut_keys")
    op.drop_table("shortcut_keys")
    op.drop_column("videos", "last_stage_update_at")
    op.drop_column("videos", "estimated_seconds_remaining")
    op.drop_column("videos", "processing_detail")
    op.drop_column("videos", "processing_stage")
    op.drop_column("videos", "is_favorited")
