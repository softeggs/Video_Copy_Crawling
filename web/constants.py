"""前端专用常量 — 与后端 constants.py 保持同步。"""

from __future__ import annotations

PENDING_STATUS = "待处理"
PROCESSING_STATUS = "处理中"
COMPLETED_STATUS = "已完成"
FAILED_STATUS = "失败"

PENDING_LIKE_STATUSES = {PENDING_STATUS, PROCESSING_STATUS}

STAGE_LABELS: dict[str, str] = {
    "queued": "排队中",
    "downloading": "下载视频",
    "transcribing": "语音转写",
    "ai_polishing": "AI 润色",
    "syncing": "同步结果",
    "completed": "已完成",
    "failed": "失败",
}

STATUS_BADGE: dict[str, str] = {
    PENDING_STATUS: "⏳",
    PROCESSING_STATUS: "🔄",
    COMPLETED_STATUS: "✅",
    FAILED_STATUS: "❌",
}
