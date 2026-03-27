from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.auth import hash_password
from backend.constants import DEFAULT_ESTIMATED_TIME, PENDING_STATUS
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models import ShortcutKey, User, Video
from backend.schemas import (
    CreateShortcutKeyRequest,
    CreateShortcutKeyResponse,
    RevokeShortcutKeyResponse,
    ShortcutKeySummaryDTO,
    ShortcutSubmitRequest,
    ShortcutSubmitResponse,
)

router = APIRouter(prefix="/shortcut-keys", tags=["shortcut-keys"])


def _isoformat(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@router.post("", response_model=CreateShortcutKeyResponse)
def create_shortcut_key(
    payload: CreateShortcutKeyRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CreateShortcutKeyResponse:
    raw_key = secrets.token_urlsafe(24)
    key_hash = hash_password(raw_key)
    key_prefix = raw_key[:8]

    record = ShortcutKey(user_id=user.id, key_hash=key_hash, key_prefix=key_prefix, name=payload.name)
    db.add(record)
    db.commit()
    db.refresh(record)

    return CreateShortcutKeyResponse(
        id=record.id,
        key=raw_key,
        key_prefix=key_prefix,
        name=record.name,
        created_at=_isoformat(record.created_at) or "",
    )


@router.get("", response_model=list[ShortcutKeySummaryDTO])
def list_shortcut_keys(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[ShortcutKeySummaryDTO]:
    keys = (
        db.execute(select(ShortcutKey).where(ShortcutKey.user_id == user.id).order_by(ShortcutKey.created_at.desc()))
        .scalars()
        .all()
    )
    return [
        ShortcutKeySummaryDTO(
            id=k.id,
            key_prefix=k.key_prefix,
            name=k.name,
            is_active=k.is_active,
            created_at=_isoformat(k.created_at) or "",
            last_used_at=_isoformat(k.last_used_at),
        )
        for k in keys
    ]


@router.delete("/{key_id}", response_model=RevokeShortcutKeyResponse)
def revoke_shortcut_key(
    key_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> RevokeShortcutKeyResponse:
    record = (
        db.execute(select(ShortcutKey).where(ShortcutKey.id == key_id, ShortcutKey.user_id == user.id))
        .scalars()
        .first()
    )
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Key not found")
    record.is_active = False
    record.revoked_at = datetime.now(timezone.utc)
    db.commit()
    return RevokeShortcutKeyResponse(id=key_id, revoked=True)


router2 = APIRouter(prefix="/shortcut-submit", tags=["shortcut-submit"])


@router2.post("", response_model=ShortcutSubmitResponse)
def shortcut_submit(
    payload: ShortcutSubmitRequest,
    db: Annotated[Session, Depends(get_db)],
) -> ShortcutSubmitResponse:
    from backend.auth import verify_password

    keys = (
        db.execute(
            select(ShortcutKey, User).join(User, ShortcutKey.user_id == User.id).where(
                ShortcutKey.is_active.is_(True), User.is_active.is_(True)
            )
        )
        .all()
    )

    for key_record, associated_user in keys:
        if verify_password(payload.key, key_record.key_hash):
            key_record.last_used_at = datetime.now(timezone.utc)
            video = Video(user_id=associated_user.id, url=payload.url, status=PENDING_STATUS)
            db.add(video)
            db.commit()
            db.refresh(video)

            return ShortcutSubmitResponse(
                success=True,
                record_id=str(video.id),
                status=PENDING_STATUS,
                estimated_time=DEFAULT_ESTIMATED_TIME,
                message=None,
            )

    return ShortcutSubmitResponse(
        success=False,
        record_id=None,
        status="",
        estimated_time=None,
        message="Invalid or revoked shortcut key",
    )
