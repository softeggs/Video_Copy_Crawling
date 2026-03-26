from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.constants import DEFAULT_VIDEO_TYPE, PENDING_STATUS
from backend.database import Base


def utc_now() -> datetime:
    """统一生成 UTC 时间，避免本地时区写入不一致。"""

    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(512))
    table_id: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    videos: Mapped[list["Video"]] = relationship("Video", back_populates="user", cascade="all, delete-orphan")


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    author: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    core_points: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    corrected_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    golden_sentences: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    video_type: Mapped[str] = mapped_column(String(255), default=DEFAULT_VIDEO_TYPE, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default=PENDING_STATUS, index=True, nullable=False)
    markdown_content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    error_msg: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship("User", back_populates="videos")

    def apply_processed_payload(self, payload: dict[str, Any], author: str, markdown_content: str) -> None:
        """将流水线处理结果写回视频记录。"""

        self.title = str(payload.get("title", self.title or ""))
        self.author = author or self.author
        self.summary = str(payload.get("summary", self.summary or ""))
        self.core_points = list(payload.get("core_points", []))
        self.corrected_text = str(payload.get("corrected_text", self.corrected_text or ""))
        self.golden_sentences = list(payload.get("golden_sentences", []))
        self.tags = list(payload.get("tags", []))
        self.video_type = str(payload.get("video_type", self.video_type or DEFAULT_VIDEO_TYPE))
        self.markdown_content = markdown_content

