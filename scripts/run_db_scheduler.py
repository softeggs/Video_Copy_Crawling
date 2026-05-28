from __future__ import annotations

import asyncio
import signal
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from utils.config import config
from utils.logger import logger

SleepCallable = Callable[[float], Awaitable[None]]
ErrorLogger = Callable[[str], None]

if TYPE_CHECKING:
    from core.db_scheduler import DatabaseScheduler


async def _pipeline_processor(url: str) -> dict[str, Any]:
    """复用现有流水线处理数据库中的待处理任务。"""

    from core.pipeline import ProcessingPipeline

    pipeline = ProcessingPipeline(
        ai_provider=config.AI_PROVIDER,
        enable_ai_polish=config.ENABLE_AI_POLISH,
        whisper_model=config.WHISPER_MODEL,
    )
    return await pipeline.process(url, progress_callback=None, skip_feishu_sync=False)


class DatabaseSchedulerService:
    """数据库调度器常驻服务。"""

    def __init__(
        self,
        scheduler: "DatabaseScheduler",
        batch_size: int,
        poll_interval_seconds: int,
        sleep_func: SleepCallable = asyncio.sleep,
        error_logger: ErrorLogger | None = None,
    ) -> None:
        self.scheduler = scheduler
        self.batch_size = batch_size
        self.poll_interval_seconds = poll_interval_seconds
        self.sleep_func = sleep_func
        self.error_logger = error_logger or logger.error
        self._stop_requested = False

    def stop(self) -> None:
        """请求停止常驻循环。"""

        self._stop_requested = True

    async def run_forever(self) -> None:
        """持续轮询数据库中的待处理任务。"""

        while not self._stop_requested:
            try:
                result = await self.scheduler.run_once(batch_size=self.batch_size)
                logger.info("数据库调度轮询完成: %s", result)
            except Exception as exc:  # noqa: BLE001 - 守护进程必须记录后继续
                self.error_logger(f"数据库调度轮询失败: {exc}")

            if self._stop_requested:
                break

            await self.sleep_func(self.poll_interval_seconds)


def build_scheduler_service() -> DatabaseSchedulerService:
    """按当前配置构建数据库调度常驻服务。"""

    from backend.database import SessionLocal
    from core.db_scheduler import DatabaseScheduler, DatabaseWritebackAdapter

    adapter = DatabaseWritebackAdapter(session_factory=SessionLocal)
    scheduler = DatabaseScheduler(
        adapter=adapter,
        processor=_pipeline_processor,
        recover_timeout_seconds=config.DB_SCHEDULER_RECOVER_TIMEOUT,
    )
    return DatabaseSchedulerService(
        scheduler=scheduler,
        batch_size=config.DB_SCHEDULER_BATCH_SIZE,
        poll_interval_seconds=config.SCHEDULER_CHECK_INTERVAL,
    )


def _register_signal_handlers(service: DatabaseSchedulerService) -> None:
    """为前台运行模式注册优雅退出信号。"""

    def _handle_signal(signum: int, frame: object | None) -> None:
        logger.info("收到退出信号 %s，准备停止数据库调度服务。", signum)
        service.stop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, _handle_signal)


async def run() -> None:
    """运行数据库调度常驻服务。"""

    service = build_scheduler_service()
    _register_signal_handlers(service)
    logger.info(
        "数据库调度服务启动: batch_size=%s, poll_interval_seconds=%s",
        service.batch_size,
        service.poll_interval_seconds,
    )
    await service.run_forever()
    logger.info("数据库调度服务已停止。")


def main() -> None:
    """命令行入口。"""

    asyncio.run(run())


if __name__ == "__main__":
    main()
