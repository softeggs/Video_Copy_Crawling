from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.constants import DEFAULT_ESTIMATED_TIME, PENDING_LIKE_STATUSES, PENDING_STATUS
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models import User, Video
from backend.schemas import (
    TypeStatDTO,
    VideoListResponse,
    VideoOverviewResponse,
    VideoRecordDTO,
    VideoSubmitRequest,
    VideoSubmitResponse,
)

router = APIRouter(prefix="/videos", tags=["videos"])


def _isoformat(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _to_video_dto(video: Video) -> VideoRecordDTO:
    return VideoRecordDTO(
        id=str(video.id),
        title=video.title,
        author=video.author,
        url=video.url,
        summary=video.summary,
        core_points=list(video.core_points or []),
        corrected_text=video.corrected_text,
        golden_sentences=list(video.golden_sentences or []),
        tags=list(video.tags or []),
        video_type=video.video_type,
        status=video.status,
        markdown_content=video.markdown_content,
        created_at=_isoformat(video.created_at) or "",
        processed_at=_isoformat(video.processed_at),
    )


@router.post("/submit", response_model=VideoSubmitResponse)
def submit_video(
    payload: VideoSubmitRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> VideoSubmitResponse:
    # URL 已在 schema 层完成标准化，这里直接落库，避免脏数据进入队列。
    video = Video(user_id=user.id, url=payload.url, status=PENDING_STATUS)
    db.add(video)
    db.commit()
    db.refresh(video)

    return VideoSubmitResponse(
        success=True,
        record_id=str(video.id),
        status=PENDING_STATUS,
        estimated_time=DEFAULT_ESTIMATED_TIME,
        message=None,
    )


@router.get("/stats", response_model=list[TypeStatDTO])
def video_stats(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[TypeStatDTO]:
    rows = db.execute(
        select(Video.video_type, func.count(Video.id))
        .where(Video.user_id == user.id)
        .group_by(Video.video_type)
    ).all()

    stats = [TypeStatDTO(video_type=video_type, count=count) for video_type, count in rows]
    return sorted(stats, key=lambda item: (-item.count, item.video_type))


@router.get("/overview", response_model=VideoOverviewResponse)
def video_overview(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> VideoOverviewResponse:
    videos = db.execute(select(Video).where(Video.user_id == user.id)).scalars().all()
    today = datetime.now(timezone.utc).date()
    today_count = sum(1 for video in videos if video.created_at.date() == today)
    pending_count = sum(1 for video in videos if video.status in PENDING_LIKE_STATUSES)

    return VideoOverviewResponse(total=len(videos), today=today_count, pending=pending_count)


@router.get("", response_model=VideoListResponse)
def list_videos(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: str | None = Query(default=None, alias="status"),
) -> VideoListResponse:
    base_query = select(Video).where(Video.user_id == user.id)
    if status_filter:
        base_query = base_query.where(Video.status == status_filter)

    total = db.execute(select(func.count()).select_from(base_query.subquery())).scalar_one()
    items = db.execute(
        base_query.order_by(Video.created_at.desc(), Video.id.desc()).offset((page - 1) * page_size).limit(page_size)
    ).scalars().all()

    return VideoListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[_to_video_dto(item) for item in items],
        has_more=page * page_size < total,
    )


@router.get("/{video_id}", response_model=VideoRecordDTO)
def get_video(
    video_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> VideoRecordDTO:
    video = db.execute(select(Video).where(Video.id == video_id, Video.user_id == user.id)).scalars().first()
    if video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    return _to_video_dto(video)
