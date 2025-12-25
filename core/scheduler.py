"""定时任务调度器 - 自动检查并处理飞书表格中的空白链接"""

import asyncio
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from .feishu_sync import FeishuSync
from .pipeline import ProcessingPipeline
from utils.logger import logger
from utils.config import config


class FeishuScheduler:
    """飞书表格定时任务调度器"""
    
    def __init__(self, check_interval: int = 300):
        """初始化调度器
        
        Args:
            check_interval: 检查间隔（秒），默认 5 分钟
        """
        self.feishu_sync = FeishuSync()
        self.check_interval = check_interval
        self.is_running = False
        self.last_check_time = None
        
    async def get_blank_records(self) -> List[Dict]:
        """获取飞书表格中的空白链接记录
        
        空白记录定义：有原始链接，但缺少标题、作者等详细信息
        
        Returns:
            空白记录列表，每条记录包含 record_id 和 url
        """
        try:
            logger.info("开始检查飞书表格中的空白链接...")
            
            # 检查必需配置
            if not all([self.feishu_sync.app_token, self.feishu_sync.table_id]):
                logger.warning("飞书配置不完整，跳过检查")
                return []
            
            from lark_oapi.api.bitable.v1 import ListAppTableRecordRequest
            
            # 获取所有记录
            request = ListAppTableRecordRequest.builder() \
                .app_token(self.feishu_sync.app_token) \
                .table_id(self.feishu_sync.table_id) \
                .page_size(500) \
                .build()
            
            response = self.feishu_sync.client.bitable.v1.app_table_record.list(request)
            
            if not response.success():
                logger.error(f"获取飞书记录失败: {response.code} - {response.msg}")
                return []
            
            blank_records = []
            
            # 筛选空白记录
            for item in response.data.items:
                fields = item.fields
                record_id = item.record_id
                
                # 提取原始链接
                url_field = fields.get("原始链接")
                if not url_field:
                    continue
                
                # 处理 URL 字段（可能是字符串或对象）
                if isinstance(url_field, dict):
                    url = url_field.get("link") or url_field.get("text")
                else:
                    url = str(url_field)
                
                if not url or not url.strip():
                    continue
                
                # 检查是否为空白记录（缺少关键信息）
                title = fields.get("标题", "").strip()
                author = fields.get("作者", "").strip()
                summary = fields.get("一句话总结", "").strip()
                status = fields.get("处理状态", "").strip()
                
                # 判断条件：有链接，但缺少标题或作者或总结，且状态不是"已完成"或"处理中"
                is_blank = (
                    url and 
                    (not title or not author or not summary) and
                    status not in ["已完成", "处理中"]
                )
                
                if is_blank:
                    blank_records.append({
                        "record_id": record_id,
                        "url": url,
                        "title": title,
                        "author": author,
                        "status": status
                    })
                    logger.info(f"发现空白记录: {url} (ID: {record_id})")
            
            logger.info(f"共发现 {len(blank_records)} 条空白记录")
            return blank_records
            
        except Exception as e:
            logger.error(f"获取空白记录失败: {str(e)}", exc_info=True)
            return []
    
    async def process_blank_record(self, record: Dict) -> bool:
        """处理单条空白记录
        
        Args:
            record: 记录信息，包含 record_id 和 url
            
        Returns:
            是否处理成功
        """
        record_id = record["record_id"]
        url = record["url"]
        
        try:
            logger.info(f"开始处理空白记录: {url}")
            
            # 更新状态为"处理中"
            await self.feishu_sync.update_record_status(record_id, "处理中")
            
            # 创建处理流水线
            pipeline = ProcessingPipeline()
            
            # 执行完整处理流程
            result = await pipeline.process(url)
            
            if result['success']:
                # 处理成功，更新飞书记录
                logger.info(f"处理成功: {url}")
                
                # 更新记录的详细信息
                await self._update_record_details(
                    record_id,
                    result['processed_content'],
                    result['metadata'],
                    result['markdown_path']
                )
                
                return True
            else:
                # 处理失败
                error_msg = result.get('error', '未知错误')
                logger.error(f"处理失败: {url} - {error_msg}")
                
                # 更新状态为"失败"
                await self.feishu_sync.update_record_status(
                    record_id, 
                    "失败", 
                    error_msg
                )
                
                return False
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"处理记录异常: {url} - {error_msg}", exc_info=True)
            
            # 更新状态为"失败"
            await self.feishu_sync.update_record_status(
                record_id,
                "失败",
                error_msg
            )
            
            return False
    
    async def _update_record_details(
        self, 
        record_id: str, 
        content: Dict, 
        metadata: Dict,
        markdown_path: str
    ):
        """更新记录的详细信息"""
        try:
            from lark_oapi.api.bitable.v1 import UpdateAppTableRecordRequest, AppTableRecord
            
            # 构建更新字段
            fields = {
                "标题": content.get('title', ''),
                "作者": metadata.get('author', ''),
                "一句话总结": content.get('summary', ''),
                "核心观点": "\n".join(content.get('core_points', [])),
                "详细内容": content.get('corrected_text', ''),
                "金句": "\n".join(content.get('golden_sentences', [])),
                "标签": content.get('tags', []),
                "笔记路径": markdown_path,
                "处理状态": "已完成",
                "处理时间": self.feishu_sync._get_current_timestamp()
            }
            
            # 添加发布日期（如果有）
            upload_date = metadata.get('upload_date', '')
            if upload_date:
                upload_date_timestamp = self.feishu_sync._convert_date_to_timestamp(upload_date)
                if upload_date_timestamp:
                    fields["发布日期"] = upload_date_timestamp
            
            # 更新记录
            request = UpdateAppTableRecordRequest.builder() \
                .app_token(self.feishu_sync.app_token) \
                .table_id(self.feishu_sync.table_id) \
                .record_id(record_id) \
                .request_body(AppTableRecord.builder()
                    .fields(fields)
                    .build()) \
                .build()
            
            response = self.feishu_sync.client.bitable.v1.app_table_record.update(request)
            
            if response.success():
                logger.info(f"记录详情更新成功: {record_id}")
            else:
                logger.error(f"记录详情更新失败: {response.code} - {response.msg}")
                
        except Exception as e:
            logger.error(f"更新记录详情异常: {str(e)}", exc_info=True)
    
    async def check_and_process(self) -> Dict:
        """检查并处理所有空白记录
        
        Returns:
            处理结果统计
        """
        start_time = time.time()
        self.last_check_time = datetime.now()
        
        logger.info("=" * 60)
        logger.info(f"开始定时检查 - {self.last_check_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # 获取空白记录
        blank_records = await self.get_blank_records()
        
        if not blank_records:
            logger.info("没有发现空白记录")
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "duration": time.time() - start_time
            }
        
        # 处理每条记录
        success_count = 0
        failed_count = 0
        
        for i, record in enumerate(blank_records, 1):
            logger.info(f"处理进度: {i}/{len(blank_records)}")
            
            success = await self.process_blank_record(record)
            
            if success:
                success_count += 1
            else:
                failed_count += 1
            
            # 避免请求过快，添加延迟
            if i < len(blank_records):
                await asyncio.sleep(2)
        
        duration = time.time() - start_time
        
        logger.info("=" * 60)
        logger.info(f"检查完成 - 耗时: {duration:.2f}秒")
        logger.info(f"总计: {len(blank_records)} | 成功: {success_count} | 失败: {failed_count}")
        logger.info("=" * 60)
        
        return {
            "total": len(blank_records),
            "success": success_count,
            "failed": failed_count,
            "duration": duration
        }
    
    async def start(self):
        """启动定时任务"""
        if self.is_running:
            logger.warning("调度器已在运行中")
            return
        
        self.is_running = True
        logger.info(f"定时任务启动 - 检查间隔: {self.check_interval}秒")
        
        try:
            while self.is_running:
                try:
                    # 执行检查和处理
                    await self.check_and_process()
                    
                    # 等待下次检查
                    logger.info(f"等待 {self.check_interval}秒后进行下次检查...")
                    await asyncio.sleep(self.check_interval)
                    
                except Exception as e:
                    logger.error(f"定时任务执行异常: {str(e)}", exc_info=True)
                    # 出错后等待一段时间再继续
                    await asyncio.sleep(60)
                    
        except asyncio.CancelledError:
            logger.info("定时任务被取消")
        finally:
            self.is_running = False
            logger.info("定时任务已停止")
    
    def stop(self):
        """停止定时任务"""
        logger.info("正在停止定时任务...")
        self.is_running = False
    
    def get_status(self) -> Dict:
        """获取调度器状态"""
        return {
            "is_running": self.is_running,
            "check_interval": self.check_interval,
            "last_check_time": self.last_check_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_check_time else None
        }
