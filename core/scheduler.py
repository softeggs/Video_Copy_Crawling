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

    RETRY_COUNT_PATTERN = r"AI_RETRY_COUNT:\s*(\d+)"
    MAX_AI_RETRY_COUNT = 10

    @staticmethod
    def _field_has_value(value) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, dict):
            return any(FeishuScheduler._field_has_value(item) for item in value.values())
        if isinstance(value, list):
            return any(FeishuScheduler._field_has_value(item) for item in value)
        return True

    def _is_pure_empty_row(self, fields: Dict) -> bool:
        return not any(self._field_has_value(value) for value in fields.values())

    @staticmethod
    def _extract_retry_count(error_msg: str) -> int:
        import re

        if not error_msg:
            return 0
        match = re.search(FeishuScheduler.RETRY_COUNT_PATTERN, error_msg)
        return int(match.group(1)) if match else 0

    def _append_retry_count(self, error_msg: str, retry_count: int) -> str:
        import re

        base_error = (error_msg or "AI polish failed").strip()
        base_error = re.sub(r"\s*AI_RETRY_COUNT:\s*\d+\s*$", "", base_error).strip()
        return f"{base_error} AI_RETRY_COUNT: {retry_count}"
        
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

                if self._is_pure_empty_row(fields):
                    deleted = await self.feishu_sync.delete_record(record_id)
                    if deleted:
                        logger.info(f"已自动删除纯空行记录: {record_id}")
                    else:
                        logger.warning(f"纯空行删除失败: {record_id}")
                    continue
                
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
            
            # 执行完整处理流程（跳过飞书同步，避免创建重复记录）
            result = await pipeline.process(url, skip_feishu_sync=True)
            
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
                "视频类型": content.get('video_type', '其他'),
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
    
    async def get_raw_transcription_records(self) -> List[Dict]:
        """获取标签中含有"原始转录"的记录
        
        这些记录是因为网络或 API 问题导致未进行 AI 润色的记录
        
        Returns:
            原始转录记录列表
        """
        try:
            logger.info("开始检查标签中含有'原始转录'的记录...")
            
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
            
            raw_records = []
            
            # 筛选含有"原始转录"标签的记录
            for item in response.data.items:
                fields = item.fields
                record_id = item.record_id
                
                # 获取标签字段
                tags = fields.get("标签", [])
                if not tags:
                    continue
                
                # 检查是否包含"原始转录"标签
                if "原始转录" in tags:
                    # 获取必要信息
                    url_field = fields.get("原始链接")
                    if not url_field:
                        continue
                    
                    # 处理 URL 字段
                    if isinstance(url_field, dict):
                        url = url_field.get("link") or url_field.get("text")
                    else:
                        url = str(url_field)
                    
                    if not url or not url.strip():
                        continue
                    
                    # 获取详细内容（原始转录文本）
                    raw_text = fields.get("详细内容", "").strip()
                    if not raw_text:
                        logger.warning(f"记录 {record_id} 标记为原始转录但没有详细内容")
                        continue
                    
                    # ??????
                    title = fields.get("??", "").strip()
                    author = fields.get("??", "").strip()
                    status = fields.get("处理状态", "").strip()
                    error_msg = fields.get("错误信息", "").strip()
                    retry_count = self._extract_retry_count(error_msg)

                    if retry_count >= self.MAX_AI_RETRY_COUNT:
                        logger.info(f"跳过记录 {record_id}，AI 失败次数已达到上限 {retry_count}")
                        continue

                    if status != "处理中":
                        raw_records.append({
                            "record_id": record_id,
                            "url": url,
                            "title": title,
                            "author": author,
                            "raw_text": raw_text,
                            "tags": tags,
                            "error_msg": error_msg,
                            "retry_count": retry_count,
                        })
                        logger.info(f"????????: {title} (ID: {record_id})")
            
            logger.info(f"共发现 {len(raw_records)} 条原始转录记录")
            return raw_records
            
        except Exception as e:
            logger.error(f"获取原始转录记录失败: {str(e)}", exc_info=True)
            return []
    
    async def reprocess_raw_transcription(self, record: Dict) -> bool:
        """重新处理原始转录记录（只做 AI 润色）
        
        Args:
            record: 记录信息，包含 record_id、raw_text 等
            
        Returns:
            是否处理成功
        """
        record_id = record["record_id"]
        title = record["title"]
        raw_text = record["raw_text"]
        retry_count = record.get("retry_count", 0)
        
        try:
            logger.info(f"开始重新处理原始转录: {title}")
            
            # 更新状态为"AI润色中"
            await self.feishu_sync.update_record_status(record_id, "AI润色中")
            
            # 创建 AI 处理器
            from .ai_processor import AIProcessor
            ai_processor = AIProcessor()
            
            # 构建元数据
            metadata = {
                'title': record.get('title', '未知标题'),
                'author': record.get('author', '未知作者'),
                'url': record.get('url', ''),
                'upload_date': '',
                'tags': []
            }
            
            # 只进行 AI 处理（不重新下载和转录）
            try:
                processed_content = await ai_processor.process(
                    raw_text,
                    metadata
                )
                
                # 生成新的 Markdown
                markdown = ai_processor.generate_markdown(
                    processed_content,
                    metadata
                )
                
                # 保存 Markdown（使用原有的文件名或创建新的）
                video_id = record_id  # 使用 record_id 作为文件名
                output_file = config.OUTPUT_PATH / f"{video_id}_reprocessed.md"
                output_file.write_text(markdown, encoding='utf-8')
                logger.info(f"重新处理的笔记已保存: {output_file}")
                
                # 更新飞书记录
                # ??????
                content_for_update = processed_content.dict()
                content_for_update["tags"] = ai_processor.build_upload_tags(
                    content_for_update.get("tags", []),
                    True
                )
                await self._update_record_with_ai_content(
                    record_id,
                    content_for_update,
                    str(output_file)
                )
                
                logger.info(f"重新处理成功: {title}")
                return True
                
            except Exception as ai_error:
                # AI 处理失败
                next_retry_count = retry_count + 1
                error_msg = self._append_retry_count(f"AI polish failed: {str(ai_error)}", next_retry_count)
                logger.error(f"{error_msg} - {title}")
                
                # 恢复状态为"已完成"（保持原始转录）
                await self.feishu_sync.update_record_status(
                    record_id,
                    "已完成",
                    error_msg
                )
                
                return False
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"重新处理异常: {title} - {error_msg}", exc_info=True)
            
            # 恢复状态为"已完成"
            await self.feishu_sync.update_record_status(
                record_id,
                "已完成",
                f"重新处理失败: {error_msg}"
            )
            
            return False
    
    async def _update_record_with_ai_content(
        self,
        record_id: str,
        content: Dict,
        markdown_path: str
    ):
        """更新记录的 AI 处理内容"""
        try:
            from lark_oapi.api.bitable.v1 import UpdateAppTableRecordRequest, AppTableRecord
            
            # 获取 AI 生成的新标签
            new_tags = content.get('tags', [])
            
            # 成功后移除重试相关标签
            new_tags = [
                tag for tag in new_tags
                if tag not in ["原始转录", "未进行AI润色标签"]
            ]
            
            logger.info(f"更新标签: 移除'原始转录'，新标签: {new_tags}")
            
            # 构建更新字段（只更新 AI 生成的内容）
            fields = {
                "一句话总结": content.get('summary', ''),
                "核心观点": "\n".join(content.get('core_points', [])),
                "详细内容": content.get('corrected_text', ''),
                "金句": "\n".join(content.get('golden_sentences', [])),
                "标签": new_tags,  # 使用过滤后的新标签（已移除"原始转录"）
                "视频类型": content.get('video_type', '其他'),
                "笔记路径": markdown_path,
                "处理状态": "已完成",
                "处理时间": self.feishu_sync._get_current_timestamp()
            }
            
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
                logger.info(f"AI 内容更新成功: {record_id}，已移除'原始转录'标签")
            else:
                logger.error(f"AI 内容更新失败: {response.code} - {response.msg}")
                
        except Exception as e:
            logger.error(f"更新 AI 内容异常: {str(e)}", exc_info=True)
    
    async def check_and_process(self) -> Dict:
        """检查并处理所有任务
        
        包括两个子任务：
        1. 处理空白链接（新记录）
        2. 重新处理原始转录记录（AI 润色）
        
        Returns:
            处理结果统计
        """
        start_time = time.time()
        self.last_check_time = datetime.now()
        
        logger.info("=" * 60)
        logger.info(f"开始定时检查 - {self.last_check_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # 任务 1: 处理空白链接
        logger.info("【任务 1】检查空白链接...")
        blank_records = await self.get_blank_records()
        
        blank_success = 0
        blank_failed = 0
        
        if blank_records:
            logger.info(f"发现 {len(blank_records)} 条空白记录，开始处理...")
            
            for i, record in enumerate(blank_records, 1):
                logger.info(f"空白记录处理进度: {i}/{len(blank_records)}")
                
                success = await self.process_blank_record(record)
                
                if success:
                    blank_success += 1
                else:
                    blank_failed += 1
                
                # 避免请求过快
                if i < len(blank_records):
                    await asyncio.sleep(2)
        else:
            logger.info("没有发现空白记录")
        
        # 任务 2: 重新处理原始转录记录
        logger.info("【任务 2】检查原始转录记录...")
        raw_records = await self.get_raw_transcription_records()
        
        raw_success = 0
        raw_failed = 0
        
        if raw_records:
            logger.info(f"发现 {len(raw_records)} 条原始转录记录，开始 AI 润色...")
            
            for i, record in enumerate(raw_records, 1):
                logger.info(f"原始转录处理进度: {i}/{len(raw_records)}")
                
                success = await self.reprocess_raw_transcription(record)
                
                if success:
                    raw_success += 1
                else:
                    raw_failed += 1
                
                # 避免请求过快
                if i < len(raw_records):
                    await asyncio.sleep(2)
        else:
            logger.info("没有发现原始转录记录")
        
        duration = time.time() - start_time
        
        # 汇总统计
        total_count = len(blank_records) + len(raw_records)
        total_success = blank_success + raw_success
        total_failed = blank_failed + raw_failed
        
        logger.info("=" * 60)
        logger.info(f"检查完成 - 耗时: {duration:.2f}秒")
        logger.info(f"【任务 1 - 空白链接】总计: {len(blank_records)} | 成功: {blank_success} | 失败: {blank_failed}")
        logger.info(f"【任务 2 - 原始转录】总计: {len(raw_records)} | 成功: {raw_success} | 失败: {raw_failed}")
        logger.info(f"【总计】总计: {total_count} | 成功: {total_success} | 失败: {total_failed}")
        logger.info("=" * 60)
        
        return {
            "total": total_count,
            "success": total_success,
            "failed": total_failed,
            "blank_total": len(blank_records),
            "blank_success": blank_success,
            "blank_failed": blank_failed,
            "raw_total": len(raw_records),
            "raw_success": raw_success,
            "raw_failed": raw_failed,
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
