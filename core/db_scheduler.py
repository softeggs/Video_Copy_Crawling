from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import Session, sessionmaker

from backend.constants import COMPLETED_STATUS, DEFAULT_VIDEO_TYPE, FAILED_STATUS, PENDING_STATUS, PROCESSING_STATUS
from backend.models import Video

ProcessorCallable = Callable[[str], Awaitable[dict[str, Any]]]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DatabaseWritebackAdapter:
    """负责数据库记录认领、回写和异常恢复。"""

    def __init__(self, session_factory: sessionmaker[Session]):
        self.session_factory = session_factory

    def list_pending_video_ids(self, batch_size: int) -> list[int]:
        with self.session_factory() as session:
            rows = session.execute(
                select(Video.id)
                .where(Video.status == PENDING_STATUS)
                .order_by(Video.created_at.asc(), Video.id.asc())
                .limit(batch_size)
            ).all()
            return [int(row[0]) for row in rows]

    def claim_video(self, video_id: int, claimed_at: datetime | None = None) -> bool:
        claimed_at = claimed_at or utc_now()
        with self.session_factory() as session:
            result = session.execute(
                update(Video)
                .where(Video.id == video_id, Video.status == PENDING_STATUS)
                .values(status=PROCESSING_STATUS, processed_at=claimed_at, error_msg="")
            )
            session.commit()
            return result.rowcount == 1

    def get_video_url(self, video_id: int) -> str | None:
        with self.session_factory() as session:
            video = session.get(Video, video_id)
            return video.url if video is not None else None

    def mark_success(self, video_id: int, result: dict[str, Any]) -> None:
        processed_content = dict(result.get("processed_content", {}))
        metadata = dict(result.get("metadata", {}))
        markdown_content = self._read_markdown(result.get("markdown_path"))

        with self.session_factory() as session:
            video = session.get(Video, video_id)
            if video is None:
                return

            video.apply_processed_payload(
                {
                    "title": processed_content.get("title", ""),
                    "summary": processed_content.get("summary", ""),
                    "core_points": list(processed_content.get("core_points", [])),
                    "corrected_text": processed_content.get("corrected_text", ""),
                    "golden_sentences": list(processed_content.get("golden_sentences", [])),
                    "tags": list(processed_content.get("tags", [])),
                    "video_type": processed_content.get("video_type", DEFAULT_VIDEO_TYPE),
                },
                author=str(metadata.get("author", video.author or "")),
                markdown_content=markdown_content,
            )
            video.status = COMPLETED_STATUS
            video.error_msg = ""
            video.processed_at = utc_now()
            session.commit()

    def mark_failure(self, video_id: int, error_msg: str) -> None:
        with self.session_factory() as session:
            video = session.get(Video, video_id)
            if video is None:
                return

            video.status = FAILED_STATUS
            video.error_msg = error_msg
            video.processed_at = utc_now()
            session.commit()

    def recover_stuck_processing(self, timeout_seconds: int, now: datetime | None = None) -> list[int]:
        now = now or utc_now()
        cutoff = now - timedelta(seconds=timeout_seconds)

        with self.session_factory() as session:
            records = session.execute(
                select(Video)
                .where(Video.status == PROCESSING_STATUS, Video.processed_at.is_not(None), Video.processed_at < cutoff)
                .order_by(Video.processed_at.asc(), Video.id.asc())
            ).scalars().all()

            recovered_ids: list[int] = []
            for video in records:
                video.status = FAILED_STATUS
                suffix = "自动收敛为失败"
                video.error_msg = f"{video.error_msg} {suffix}".strip() if video.error_msg else suffix
                recovered_ids.append(int(video.id))
            session.commit()
            return recovered_ids

    def get_snapshot(self) -> dict[str, int]:
        with self.session_factory() as session:
            rows = session.execute(select(Video.status)).all()
        counts: dict[str, int] = {}
        for (status,) in rows:
            counts[status] = counts.get(status, 0) + 1
        return counts

    @staticmethod
    def _read_markdown(markdown_path: str | None) -> str:
        if not markdown_path:
            return ""

        path = Path(markdown_path)
        if not path.exists():
            return ""

        return path.read_text(encoding="utf-8")


class DatabaseScheduler:
    """基于数据库状态字段驱动的简化任务调度器。"""

    def __init__(
        self,
        adapter: DatabaseWritebackAdapter,
        processor: ProcessorCallable,
        recover_timeout_seconds: int = 3600,
    ) -> None:
        self.adapter = adapter
        self.processor = processor
        self.recover_timeout_seconds = recover_timeout_seconds

    async def process_video_by_id(self, video_id: int) -> dict[str, Any]:
        claimed = self.adapter.claim_video(video_id)
        if not claimed:
            return {"video_id": video_id, "claimed": False, "success": False}

        url = self.adapter.get_video_url(video_id)
        if not url:
            self.adapter.mark_failure(video_id, "missing-video-url")
            return {"video_id": video_id, "claimed": True, "success": False, "error": "missing-video-url"}

        try:
            result = await self.processor(url)
        except Exception as exc:  # noqa: BLE001 - 调度层需要兜底
            self.adapter.mark_failure(video_id, str(exc))
            return {"video_id": video_id, "claimed": True, "success": False, "error": str(exc)}

        if result.get("success"):
            self.adapter.mark_success(video_id, result)
            return {"video_id": video_id, "claimed": True, "success": True}

        error_msg = str(result.get("error", "processor-failed"))
        self.adapter.mark_failure(video_id, error_msg)
        return {"video_id": video_id, "claimed": True, "success": False, "error": error_msg}

    async def run_once(self, batch_size: int = 10) -> dict[str, int]:
        self.adapter.recover_stuck_processing(timeout_seconds=self.recover_timeout_seconds)
        pending_ids = self.adapter.list_pending_video_ids(batch_size=batch_size)

        summary = {"processed": 0, "success": 0, "failed": 0, "skipped": 0}
        for video_id in pending_ids:
            result = await self.process_video_by_id(video_id)
            if not result.get("claimed"):
                summary["skipped"] += 1
                continue

            summary["processed"] += 1
            if result.get("success"):
                summary["success"] += 1
            else:
                summary["failed"] += 1

        return summary

