"""飞书表格定时任务 - 独立运行脚本

自动检查飞书表格中的空白链接并处理
可以作为后台服务运行
"""

import asyncio
import signal
import sys
from core.scheduler import FeishuScheduler
from utils.logger import logger
from utils.config import config


def signal_handler(signum, frame):
    """处理退出信号"""
    logger.info("收到退出信号，正在停止...")
    sys.exit(0)


async def main():
    """主函数"""
    # 检查飞书配置
    if not all([
        config.FEISHU_APP_ID,
        config.FEISHU_APP_SECRET,
        config.FEISHU_BITABLE_APP_TOKEN,
        config.FEISHU_BITABLE_TABLE_ID
    ]):
        logger.error("飞书配置不完整，请检查 .env 文件")
        logger.error("需要配置: FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_BITABLE_APP_TOKEN, FEISHU_BITABLE_TABLE_ID")
        return
    
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 创建调度器（默认 5 分钟检查一次）
    check_interval = 300  # 5 分钟
    scheduler = FeishuScheduler(check_interval=check_interval)
    
    logger.info("=" * 60)
    logger.info("飞书表格定时任务启动")
    logger.info(f"检查间隔: {check_interval}秒 ({check_interval // 60}分钟)")
    logger.info("按 Ctrl+C 停止")
    logger.info("=" * 60)
    
    try:
        # 启动定时任务
        await scheduler.start()
    except KeyboardInterrupt:
        logger.info("收到键盘中断信号")
    finally:
        scheduler.stop()
        logger.info("定时任务已停止")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序退出")
