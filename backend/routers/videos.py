from collections import Counter
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_current_user, get_db


router = APIRouter(prefix="/videos", tags=["videos"])
VALID_STATUSES = {"待处理", "处理中", "已完成", "失败"}


def _iso(dt: datetime | None) -> str | None:
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def _to_video_response(video: models.Video) -> schemas.VideoRecordResponse:
    return schemas.VideoRecordResponse(
        id=str(video.id),
        title=video.title or "",
        author=video.author or "",
        url=video.url,
        summary=video.summary or "",
        core_points=video.core_points or [],
        corrected_text=video.corrected_text or "",
        golden_sentences=video.golden_sentences or [],
        tags=video.tags or [],
        video_type=video.video_type or "其他",
        status=video.status,
        markdown_content=video.markdown_content or "",
        created_at=_iso(video.created_at) or "",
        processed_at=_iso(video.processed_at),
    )


@router.post("/submit", response_model=schemas.VideoSubmitResponse)
def submit_video(
    payload: schemas.VideoSubmitRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.VideoSubmitResponse:
    video = models.Video(
        user_id=current_user.id,
        url=payload.url.strip(),
        status="待处理",
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    return schemas.VideoSubmitResponse(
        success=True,
        record_id=str(video.id),
        status=video.status,
        estimated_time="2-5分钟",
        message=None,
    )


@router.get("", response_model=schemas.VideoListResponse)
def list_videos(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.VideoListResponse:
    query = db.query(models.Video).filter(models.Video.user_id == current_user.id)
    if status_filter:
        query = query.filter(models.Video.status == status_filter)

    total = query.count()
    items = (
        query.order_by(desc(models.Video.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    has_more = page * page_size < total

    return schemas.VideoListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[_to_video_response(item) for item in items],
        has_more=has_more,
    )


@router.get("/{video_id}", response_model=schemas.VideoRecordResponse)
def get_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.VideoRecordResponse:
    video = (
        db.query(models.Video)
        .filter(models.Video.id == video_id, models.Video.user_id == current_user.id)
        .first()
    )
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    return _to_video_response(video)


@router.get("/stats", response_model=list[schemas.TypeStatResponse])
def video_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> list[schemas.TypeStatResponse]:
    videos = db.query(models.Video).filter(models.Video.user_id == current_user.id).all()
    counter = Counter((video.video_type or "其他") for video in videos)
    return [
        schemas.TypeStatResponse(video_type=video_type, count=count)
        for video_type, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


@router.get("/overview", response_model=schemas.VideoOverviewResponse)
def video_overview(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.VideoOverviewResponse:
    videos = db.query(models.Video).filter(models.Video.user_id == current_user.id).all()

    today_str = datetime.now(timezone.utc).date().isoformat()
    today = sum(1 for video in videos if (_iso(video.created_at) or "").startswith(today_str))
    pending = sum(1 for video in videos if video.status in {"待处理", "处理中"})

    return schemas.VideoOverviewResponse(total=len(videos), today=today, pending=pending)
