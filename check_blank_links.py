"""手动检查并处理飞书表格中的空白链接

一次性执行，适合手动触发或测试
"""

import asyncio
from core.scheduler import FeishuScheduler
from utils.logger import logger
from utils.config import config


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
    
    # 创建调度器
    scheduler = FeishuScheduler()
    
    logger.info("开始手动检查飞书表格中的空白链接...")
    
    # 执行一次检查和处理
    result = await scheduler.check_and_process()
    
    # 输出结果
    print("\n" + "=" * 60)
    print("处理结果:")
    print(f"  总计: {result['total']} 条")
    print(f"  成功: {result['success']} 条")
    print(f"  失败: {result['failed']} 条")
    print(f"  耗时: {result['duration']:.2f} 秒")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
