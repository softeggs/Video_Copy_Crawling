"""统一 API 调用层 — 对标 iOS APIService，所有 Web 接口走此模块。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import requests

from utils.config import config


class APIError(Exception):
    """统一 API 异常。"""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@dataclass
class _UserDTO:
    user_id: str
    username: str
    display_name: str
    table_id: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> _UserDTO:
        return cls(
            user_id=data.get("user_id", ""),
            username=data.get("username", ""),
            display_name=data.get("display_name", ""),
            table_id=data.get("table_id", ""),
        )


@dataclass
class LoginResponse:
    token: str
    user: _UserDTO


@dataclass
class VideoRecordDTO:
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
    is_favorited: bool = False
    processing_stage: str = ""
    processing_detail: str = ""
    estimated_seconds_remaining: int | None = None
    last_stage_update_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VideoRecordDTO:
        return cls(
            id=data.get("id", ""),
            title=data.get("title", "") or "未命名视频",
            author=data.get("author", "") or "未知作者",
            url=data.get("url", ""),
            summary=data.get("summary", ""),
            core_points=data.get("core_points") or [],
            corrected_text=data.get("corrected_text", ""),
            golden_sentences=data.get("golden_sentences") or [],
            tags=data.get("tags") or [],
            video_type=data.get("video_type", ""),
            status=data.get("status", ""),
            markdown_content=data.get("markdown_content", ""),
            created_at=data.get("created_at", ""),
            processed_at=data.get("processed_at"),
            is_favorited=data.get("is_favorited", False),
            processing_stage=data.get("processing_stage", ""),
            processing_detail=data.get("processing_detail", ""),
            estimated_seconds_remaining=data.get("estimated_seconds_remaining"),
            last_stage_update_at=data.get("last_stage_update_at"),
        )


@dataclass
class VideoListResponse:
    total: int
    page: int
    page_size: int
    items: list[VideoRecordDTO]
    has_more: bool


@dataclass
class VideoOverviewResponse:
    total: int
    today: int
    pending: int


@dataclass
class TypeStatDTO:
    video_type: str
    count: int


@dataclass
class VideoSubmitResponse:
    success: bool
    record_id: str
    status: str
    estimated_time: str | None
    message: str | None


@dataclass
class VideoStatusDTO:
    id: str
    status: str
    processing_stage: str
    processing_detail: str
    estimated_seconds_remaining: int | None
    last_stage_update_at: str | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VideoStatusDTO:
        return cls(
            id=data.get("id", ""),
            status=data.get("status", ""),
            processing_stage=data.get("processing_stage", ""),
            processing_detail=data.get("processing_detail", ""),
            estimated_seconds_remaining=data.get("estimated_seconds_remaining"),
            last_stage_update_at=data.get("last_stage_update_at"),
        )


@dataclass
class FavoriteResponse:
    id: str
    is_favorited: bool


@dataclass
class ShortcutKeySummaryDTO:
    id: int
    key_prefix: str
    name: str
    is_active: bool
    created_at: str
    last_used_at: str | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ShortcutKeySummaryDTO:
        return cls(
            id=data.get("id", 0),
            key_prefix=data.get("key_prefix", ""),
            name=data.get("name", ""),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", ""),
            last_used_at=data.get("last_used_at"),
        )


@dataclass
class CreateShortcutKeyResponse:
    id: int
    key: str
    key_prefix: str
    name: str
    created_at: str


@dataclass
class ShortcutSubmitResponse:
    success: bool
    record_id: str | None
    status: str
    estimated_time: str | None
    message: str | None


class APIClient:
    """统一 API 调用封装，对标 iOS APIService。"""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or config.API_BASE_URL).rstrip("/")
        self._token: str | None = None

    def set_token(self, token: str | None) -> None:
        self._token = token

    def _headers(self, authenticated: bool = True) -> dict[str, str]:
        headers: dict[str, str] = {"Accept": "application/json", "Content-Type": "application/json"}
        if authenticated and self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _handle_error(self, response: requests.Response) -> None:
        if response.status_code == 401:
            raise APIError("鉴权失败，请重新登录。", status_code=401)
        try:
            detail = response.json().get("detail", "")
            if isinstance(detail, list):
                detail = "; ".join(d.get("msg", "") or str(d) for d in detail)
        except Exception:
            detail = response.text or response.reason
        raise APIError(str(detail) or response.reason, status_code=response.status_code)

    def _request(
        self,
        method: str,
        path: str,
        authenticated: bool = True,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self._headers(authenticated),
                params=params,
                json=json_data,
                timeout=15,
            )
        except requests.RequestException as exc:
            raise APIError(f"网络请求失败：{exc}") from exc

        if not (200 <= response.status_code < 300):
            self._handle_error(response)

        return response.json()

    # ---- Auth ----

    def login(self, username: str, password: str) -> LoginResponse:
        data = self._request("POST", "/auth/login", authenticated=False, json_data={"username": username, "password": password})
        return LoginResponse(
            token=data["token"],
            user=_UserDTO.from_dict(data["user"]),
        )

    def register(self, username: str, email: str, display_name: str, password: str) -> LoginResponse:
        data = self._request(
            "POST",
            "/auth/register",
            authenticated=False,
            json_data={
                "username": username,
                "email": email,
                "display_name": display_name,
                "password": password,
            },
        )
        return LoginResponse(token=data["token"], user=_UserDTO.from_dict(data["user"]))

    # ---- Videos ----

    def get_overview(self) -> VideoOverviewResponse:
        data = self._request("GET", "/videos/overview")
        return VideoOverviewResponse(**data)

    def get_stats(self) -> list[TypeStatDTO]:
        data = self._request("GET", "/videos/stats")
        return [TypeStatDTO(**item) for item in data]

    def get_videos(self, page: int = 1, page_size: int = 20, status: str | None = None) -> VideoListResponse:
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status
        data = self._request("GET", "/videos", params=params)
        return VideoListResponse(
            total=data["total"],
            page=data["page"],
            page_size=data["page_size"],
            items=[VideoRecordDTO.from_dict(item) for item in data["items"]],
            has_more=data["has_more"],
        )

    def get_video(self, video_id: int | str) -> VideoRecordDTO:
        data = self._request("GET", f"/videos/{video_id}")
        return VideoRecordDTO.from_dict(data)

    def submit_video(self, url: str) -> VideoSubmitResponse:
        data = self._request("POST", "/videos/submit", json_data={"url": url, "table_id": ""})
        return VideoSubmitResponse(**data)

    def delete_video(self, video_id: int | str) -> None:
        self._request("DELETE", f"/videos/{video_id}")
        return None

    def toggle_favorite(self, video_id: int | str, is_favorited: bool) -> FavoriteResponse:
        data = self._request("POST", f"/videos/{video_id}/favorite", json_data={"is_favorited": is_favorited})
        return FavoriteResponse(**data)

    def get_video_status(self, video_id: int | str) -> VideoStatusDTO:
        data = self._request("GET", f"/videos/{video_id}/status")
        return VideoStatusDTO.from_dict(data)

    # ---- Shortcut Keys ----

    def list_shortcut_keys(self) -> list[ShortcutKeySummaryDTO]:
        data = self._request("GET", "/shortcut-keys")
        return [ShortcutKeySummaryDTO.from_dict(item) for item in data]

    def create_shortcut_key(self, name: str = "快捷指令密钥") -> CreateShortcutKeyResponse:
        data = self._request("POST", "/shortcut-keys", json_data={"name": name})
        return CreateShortcutKeyResponse(**data)

    def revoke_shortcut_key(self, key_id: int) -> bool:
        data = self._request("DELETE", f"/shortcut-keys/{key_id}")
        return data.get("revoked", False)

    def shortcut_submit(self, key: str, url: str) -> ShortcutSubmitResponse:
        data = self._request("POST", "/shortcut-submit", authenticated=False, json_data={"key": key, "url": url})
        return ShortcutSubmitResponse(**data)


api_client = APIClient()
