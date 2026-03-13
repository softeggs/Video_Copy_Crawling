from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import hash_password
from ..dependencies import get_admin_user, get_db


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[schemas.UserAdminResponse])
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_admin_user),
) -> list[schemas.UserAdminResponse]:
    return (
        db.query(models.User)
        .order_by(models.User.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )


@router.post("/users", response_model=schemas.UserAdminResponse)
def create_user(
    payload: schemas.UserAdminCreateRequest,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_admin_user),
) -> schemas.UserAdminResponse:
    exists = (
        db.query(models.User)
        .filter((models.User.username == payload.username) | (models.User.email == payload.email))
        .first()
    )
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already exists")

    user = models.User(
        username=payload.username,
        email=payload.email,
        display_name=payload.display_name,
        password_hash=hash_password(payload.password),
        is_admin=payload.is_admin,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=schemas.UserAdminResponse)
def update_user(
    user_id: int,
    payload: schemas.UserAdminUpdateRequest,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_admin_user),
) -> schemas.UserAdminResponse:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.display_name is not None:
        user.display_name = payload.display_name
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.is_admin is not None:
        user.is_admin = payload.is_admin

    db.commit()
    db.refresh(user)
    return user


@router.get("/videos/pending", response_model=list[schemas.VideoRecordResponse])
def pending_videos(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_admin_user),
) -> list[schemas.VideoRecordResponse]:
    items = (
        db.query(models.Video)
        .filter(models.Video.status.in_(["待处理", "处理中"]))
        .order_by(models.Video.created_at.asc())
        .all()
    )
    return [
        schemas.VideoRecordResponse(
            id=str(item.id),
            title=item.title,
            author=item.author,
            url=item.url,
            summary=item.summary,
            core_points=item.core_points or [],
            corrected_text=item.corrected_text,
            golden_sentences=item.golden_sentences or [],
            tags=item.tags or [],
            video_type=item.video_type,
            status=item.status,
            markdown_content=item.markdown_content,
            created_at=item.created_at.isoformat(),
            processed_at=item.processed_at.isoformat() if item.processed_at else None,
        )
        for item in items
    ]


@router.get("/stats")
def admin_stats(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_admin_user),
) -> dict:
    total_users = db.query(models.User).count()
    active_users = db.query(models.User).filter(models.User.is_active.is_(True)).count()
    total_videos = db.query(models.Video).count()
    pending_videos = db.query(models.Video).filter(models.Video.status.in_(["待处理", "处理中"]))
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_videos": total_videos,
        "pending_videos": pending_videos.count(),
    }


@router.get("/api-balance")
def api_balance(_: models.User = Depends(get_admin_user)) -> dict:
    return {
        "openai": "unknown",
        "kimi": "unknown",
        "gemini": "unknown",
    }


@router.post("/cleanup")
def cleanup_processed_content(
    days: int = Query(default=30, ge=1),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_admin_user),
) -> dict:
    threshold = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(models.Video)
        .filter(models.Video.status == "已完成", models.Video.processed_at.is_not(None), models.Video.processed_at < threshold)
        .all()
    )

    for row in rows:
        row.corrected_text = ""
        row.markdown_content = ""

    db.commit()
    return {"success": True, "cleaned_records": len(rows), "days": days}
