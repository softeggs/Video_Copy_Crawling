from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator

from backend.video_url import normalize_video_url


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    email: EmailStr
    display_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class UserDTO(BaseModel):
    user_id: str
    username: str
    display_name: str
    table_id: str


class LoginResponse(BaseModel):
    token: str
    user: UserDTO


class VideoSubmitRequest(BaseModel):
    url: str = Field(min_length=1)
    table_id: str | None = ""

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        """在进入业务逻辑前完成 URL 归一化。"""

        return normalize_video_url(value)


class VideoSubmitResponse(BaseModel):
    success: bool
    record_id: str
    status: str
    estimated_time: str | None
    message: str | None


class VideoRecordDTO(BaseModel):
    id: str
    title: str
    author: str
    url: str
    summary: str
    core_points: list[str]
    corrected_text: str
    golden_sentences: list[str]
    tags: list[str]
    video_type: str
    status: str
    markdown_content: str
    created_at: str
    processed_at: str | None
    # P3 新增字段
    is_favorited: bool = False
    processing_stage: str = ""
    processing_detail: str = ""
    estimated_seconds_remaining: int | None = None
    last_stage_update_at: str | None = None


class VideoListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[VideoRecordDTO]
    has_more: bool


class TypeStatDTO(BaseModel):
    video_type: str
    count: int


class VideoOverviewResponse(BaseModel):
    total: int
    today: int
    pending: int


class AdminUserDTO(BaseModel):
    id: int
    username: str
    email: str
    display_name: str
    is_active: bool
    is_admin: bool
    created_at: str


class AdminStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_videos: int
    pending_videos: int


class CleanupResponse(BaseModel):
    success: bool
    cleaned_records: int
    days: int


class HealthResponse(BaseModel):
    status: str
    database_url: str
    service: str


# ========== P3 新增 ==========


class VideoStatusDTO(BaseModel):
    """轻量级状态轮询响应。"""

    id: str
    status: str
    processing_stage: str
    processing_detail: str
    estimated_seconds_remaining: int | None = None
    last_stage_update_at: str | None = None


class FavoriteRequest(BaseModel):
    is_favorited: bool


class FavoriteResponse(BaseModel):
    id: str
    is_favorited: bool


class ShortcutKeySummaryDTO(BaseModel):
    """密钥摘要，用于列表展示（不暴露明文）。"""

    id: int
    key_prefix: str
    name: str
    is_active: bool
    created_at: str
    last_used_at: str | None = None


class CreateShortcutKeyRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255, default="快捷指令密钥")


class CreateShortcutKeyResponse(BaseModel):
    """创建密钥时一次性返回明文，之后服务端不再留存。"""

    id: int
    key: str
    key_prefix: str
    name: str
    created_at: str


class RevokeShortcutKeyResponse(BaseModel):
    id: int
    revoked: bool


class ShortcutSubmitRequest(BaseModel):
    key: str = Field(min_length=1)
    url: str = Field(min_length=1)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        return normalize_video_url(value)


class ShortcutSubmitResponse(BaseModel):
    success: bool
    record_id: str | None = None
    status: str
    estimated_time: str | None = None
    message: str | None = None
