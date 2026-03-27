from __future__ import annotations

PENDING_STATUS = "待处理"
PROCESSING_STATUS = "处理中"
COMPLETED_STATUS = "已完成"
FAILED_STATUS = "失败"

DEFAULT_VIDEO_TYPE = "其他"
DEFAULT_ESTIMATED_TIME = "2-5分钟"

PENDING_LIKE_STATUSES = {PENDING_STATUS, PROCESSING_STATUS}

# 处理阶段（供 processing_stage 字段使用）
STAGE_QUEUED = "queued"
STAGE_DOWNLOADING = "downloading"
STAGE_TRANSCRIBING = "transcribing"
STAGE_AI_POLISHING = "ai_polishing"
STAGE_SYNCING = "syncing"
STAGE_COMPLETED = "completed"
STAGE_FAILED = "failed"

STAGE_LABELS: dict[str, str] = {
    STAGE_QUEUED: "排队中",
    STAGE_DOWNLOADING: "下载视频",
    STAGE_TRANSCRIBING: "语音转写",
    STAGE_AI_POLISHING: "AI 润色",
    STAGE_SYNCING: "同步结果",
    STAGE_COMPLETED: "已完成",
    STAGE_FAILED: "失败",
}

