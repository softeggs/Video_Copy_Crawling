"""后台定时任务管理器 - 用于 Streamlit 应用

在 Streamlit 应用中运行后台定时任务
"""

import asyncio
import threading
import time
from datetime import datetime
from typing import Optional, Dict
from .scheduler import FeishuScheduler
from utils.logger import logger


class BackgroundScheduler:
    """后台定时任务管理器（线程安全）"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化管理器"""
        if not hasattr(self, 'initialized'):
            self.scheduler = None
            self.thread = None
            self.is_running = False
            self.check_interval = 300  # 默认 5 分钟
            self.last_result = None
            self.last_check_time = None
            self.initialized = True
    
    def start(self, check_interval: int = 300) -> Dict:
        """启动后台定时任务
        
        Args:
            check_interval: 检查间隔（秒）
            
        Returns:
            启动结果
        """
        if self.is_running:
            return {
                'success': False,
                'message': '定时任务已在运行中'
            }
        
        try:
            self.check_interval = check_interval
            self.is_running = True
            
            # 创建并启动后台线程
            self.thread = threading.Thread(
                target=self._run_scheduler,
                daemon=True  # 守护线程，主程序退出时自动结束
            )
            self.thread.start()
            
            logger.info(f"后台定时任务已启动，检查间隔: {check_interval}秒")
            
            return {
                'success': True,
                'message': f'定时任务已启动（每 {check_interval // 60} 分钟检查一次）'
            }
            
        except Exception as e:
            self.is_running = False
            logger.error(f"启动后台定时任务失败: {str(e)}")
            return {
                'success': False,
                'message': f'启动失败: {str(e)}'
            }
    
    def stop(self) -> Dict:
        """停止后台定时任务
        
        Returns:
            停止结果
        """
        if not self.is_running:
            return {
                'success': False,
                'message': '定时任务未运行'
            }
        
        try:
            self.is_running = False
            
            # 等待线程结束（最多等待 5 秒）
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=5)
            
            logger.info("后台定时任务已停止")
            
            return {
                'success': True,
                'message': '定时任务已停止'
            }
            
        except Exception as e:
            logger.error(f"停止后台定时任务失败: {str(e)}")
            return {
                'success': False,
                'message': f'停止失败: {str(e)}'
            }
    
    def get_status(self) -> Dict:
        """获取定时任务状态
        
        Returns:
            状态信息
        """
        return {
            'is_running': self.is_running,
            'check_interval': self.check_interval,
            'check_interval_minutes': self.check_interval // 60,
            'last_check_time': self.last_check_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_check_time else None,
            'last_result': self.last_result
        }
    
    def _run_scheduler(self):
        """在后台线程中运行定时任务"""
        logger.info("后台定时任务线程启动")
        
        # 创建新的事件循环（因为在新线程中）
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            while self.is_running:
                try:
                    # 执行检查和处理
                    self.last_check_time = datetime.now()
                    logger.info(f"开始定时检查 - {self.last_check_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # 创建调度器
                    scheduler = FeishuScheduler(check_interval=self.check_interval)
                    
                    # 执行检查（使用新的事件循环）
                    result = loop.run_until_complete(scheduler.check_and_process())
                    
                    # 保存结果
                    self.last_result = result
                    
                    logger.info(f"定时检查完成 - 总计: {result['total']}, 成功: {result['success']}, 失败: {result['failed']}")
                    
                    # 等待下次检查
                    wait_time = 0
                    while wait_time < self.check_interval and self.is_running:
                        time.sleep(1)
                        wait_time += 1
                    
                except Exception as e:
                    logger.error(f"定时任务执行异常: {str(e)}", exc_info=True)
                    # 出错后等待一段时间再继续
                    time.sleep(60)
        
        finally:
            loop.close()
            logger.info("后台定时任务线程结束")
    
    def execute_once(self) -> Dict:
        """立即执行一次检查（不影响定时任务）
        
        Returns:
            执行结果
        """
        try:
            logger.info("手动触发检查")
            
            # 创建调度器
            scheduler = FeishuScheduler()
            
            # 执行检查
            result = asyncio.run(scheduler.check_and_process())
            
            # 更新最后检查时间和结果
            self.last_check_time = datetime.now()
            self.last_result = result
            
            return {
                'success': True,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"手动检查失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': str(e)
            }


# 全局单例实例
background_scheduler = BackgroundScheduler()
