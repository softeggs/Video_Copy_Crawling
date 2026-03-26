from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.constants import COMPLETED_STATUS, PENDING_LIKE_STATUSES
from backend.database import get_db
from backend.dependencies import get_current_admin
from backend.models import User, Video
from backend.schemas import AdminStatsResponse, AdminUserDTO, CleanupResponse, VideoRecordDTO
from backend.routers.videos import _to_video_dto, _isoformat
from utils.config import config

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[AdminUserDTO])
def list_users(
    _: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> list[AdminUserDTO]:
    users = db.execute(select(User).order_by(User.created_at.asc(), User.id.asc())).scalars().all()
    return [
        AdminUserDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            display_name=user.display_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=_isoformat(user.created_at) or "",
        )
        for user in users
    ]


@router.get("/videos/pending", response_model=list[VideoRecordDTO])
def list_pending_videos(
    _: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> list[VideoRecordDTO]:
    videos = db.execute(
        select(Video)
        .where(Video.status.in_(tuple(PENDING_LIKE_STATUSES)))
        .order_by(Video.created_at.asc(), Video.id.asc())
    ).scalars().all()
    return [_to_video_dto(video) for video in videos]


@router.get("/stats", response_model=AdminStatsResponse)
def admin_stats(
    _: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> AdminStatsResponse:
    total_users = db.execute(select(func.count(User.id))).scalar_one()
    active_users = db.execute(select(func.count(User.id)).where(User.is_active.is_(True))).scalar_one()
    total_videos = db.execute(select(func.count(Video.id))).scalar_one()
    pending_videos = db.execute(select(func.count(Video.id)).where(Video.status.in_(tuple(PENDING_LIKE_STATUSES)))).scalar_one()
    return AdminStatsResponse(
        total_users=total_users,
        active_users=active_users,
        total_videos=total_videos,
        pending_videos=pending_videos,
    )


@router.get("/api-balance")
def api_balance(_: Annotated[User, Depends(get_current_admin)]) -> dict[str, object]:
    return {
        "is_placeholder": True,
        "message": "API balance aggregation is not implemented yet for the rebuilt backend.",
        "providers": {"openai": "unknown", "kimi": "unknown", "gemini": "unknown"},
    }


@router.post("/cleanup", response_model=CleanupResponse)
def cleanup_content(
    _: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
    days: int = Query(default_factory=lambda: config.CLEANUP_DAYS_DEFAULT, ge=1),
) -> CleanupResponse:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    records = db.execute(
        select(Video).where(Video.status == COMPLETED_STATUS, Video.processed_at.is_not(None), Video.processed_at < cutoff)
    ).scalars().all()

    for video in records:
        video.corrected_text = ""
        video.markdown_content = ""

    db.commit()
    return CleanupResponse(success=True, cleaned_records=len(records), days=days)

