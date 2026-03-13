from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str
    email: EmailStr
    display_name: str


class UserRegisterRequest(UserBase):
    password: str = Field(min_length=6)


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    username: str
    display_name: str
    table_id: str = ""


class LoginResponse(BaseModel):
    token: str
    user: UserResponse


class MessageResponse(BaseModel):
    success: bool
    message: str


class VideoSubmitRequest(BaseModel):
    url: str
    table_id: str | None = ""


class VideoSubmitResponse(BaseModel):
    success: bool
    record_id: str
    status: str
    estimated_time: str | None = None
    message: str | None = None


class VideoRecordResponse(BaseModel):
    id: str
    title: str = ""
    author: str = ""
    url: str
    summary: str = ""
    core_points: list[str] = Field(default_factory=list)
    corrected_text: str = ""
    golden_sentences: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    video_type: str = "其他"
    status: str
    markdown_content: str = ""
    created_at: str
    processed_at: str | None = None


class VideoListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[VideoRecordResponse]
    has_more: bool


class TypeStatResponse(BaseModel):
    video_type: str
    count: int


class VideoOverviewResponse(BaseModel):
    total: int
    today: int
    pending: int


class UserAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    display_name: str
    is_active: bool
    is_admin: bool
    created_at: datetime


class UserAdminCreateRequest(BaseModel):
    username: str
    email: EmailStr
    display_name: str
    password: str = Field(min_length=6)
    is_admin: bool = False


class UserAdminUpdateRequest(BaseModel):
    display_name: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None
