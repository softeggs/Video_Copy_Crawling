import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *
from typing import Dict
from utils.logger import logger
from utils.config import config
from utils.network import disable_proxy_env

class FeishuSync:
    def __init__(self):
        # 创建客户端，禁用 SSL 验证（Docker 环境中可能需要）
        self.client = lark.Client.builder() \
            .app_id(config.FEISHU_APP_ID) \
            .app_secret(config.FEISHU_APP_SECRET) \
            .log_level(lark.LogLevel.ERROR) \
            .build()
        
        self.app_token = config.FEISHU_BITABLE_APP_TOKEN
        self.table_id = config.FEISHU_BITABLE_TABLE_ID
    
    async def sync_to_bitable(self, content: Dict, metadata: Dict, markdown_path: str) -> bool:
        """同步到飞书多维表格"""
        try:
            logger.info("开始同步到飞书")
            
            # 检查必需配置
            if not all([self.app_token, self.table_id]):
                logger.warning("飞书配置不完整，跳过同步")
                return False
            
            # 构建记录字段
            # 注意：URL 字段需要特殊格式
            url = metadata.get('url', '')
            url_field = {
                "link": url,
                "text": url  # 显示文本
            } if url else None
            
            # 转换发布日期为时间戳
            upload_date = metadata.get('upload_date', '')
            upload_date_timestamp = self._convert_date_to_timestamp(upload_date) if upload_date else None
            
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
                "处理时间": self._get_current_timestamp()
            }
            
            # 只有当 URL 存在时才添加
            if url_field:
                fields["原始链接"] = url_field
            
            # 只有当发布日期存在时才添加
            if upload_date_timestamp:
                fields["发布日期"] = upload_date_timestamp
            
            # 创建记录
            request = CreateAppTableRecordRequest.builder() \
                .app_token(self.app_token) \
                .table_id(self.table_id) \
                .request_body(AppTableRecord.builder()
                    .fields(fields)
                    .build()) \
                .build()
            
            with disable_proxy_env():
                response = self.client.bitable.v1.app_table_record.create(request)
            
            if not response.success():
                logger.error(f"飞书同步失败: {response.code} - {response.msg}")
                logger.error(f"详细错误: {response.error}")
                return False
            
            logger.info(f"飞书同步成功，记录 ID: {response.data.record.record_id}")
            return True
            
        except Exception as e:
            logger.error(f"飞书同步异常: {str(e)}", exc_info=True)
            return False
    
    async def update_record_status(self, record_id: str, status: str, error_msg: str = None, tags: list[str] = None):
        """更新记录状态"""
        try:
            fields = {"处理状态": status}
            if error_msg:
                fields["错误信息"] = error_msg
            if tags is not None:
                fields["标签"] = tags
            
            request = UpdateAppTableRecordRequest.builder() \
                .app_token(self.app_token) \
                .table_id(self.table_id) \
                .record_id(record_id) \
                .request_body(AppTableRecord.builder()
                    .fields(fields)
                    .build()) \
                .build()
            
            with disable_proxy_env():
                response = self.client.bitable.v1.app_table_record.update(request)
            return response.success()
            
        except Exception as e:
            logger.error(f"更新记录状态失败: {str(e)}")
            return False
    
    async def delete_record(self, record_id: str) -> bool:
        """?????????????"""
        try:
            request = DeleteAppTableRecordRequest.builder() \
                .app_token(self.app_token) \
                .table_id(self.table_id) \
                .record_id(record_id) \
                .build()

            with disable_proxy_env():
                response = self.client.bitable.v1.app_table_record.delete(request)
            return response.success()
        except Exception as e:
            logger.error(f"????????: {str(e)}")
            return False

    @staticmethod
    def _get_current_timestamp() -> int:
        """获取当前时间戳（毫秒）"""
        import time
        return int(time.time() * 1000)
    
    @staticmethod
    def _convert_date_to_timestamp(date_str: str) -> int:
        """将日期字符串转换为 Unix 时间戳（毫秒）
        
        Args:
            date_str: 日期字符串，格式如 '2024-01-01' 或 '20240101'
            
        Returns:
            Unix 时间戳（毫秒）
        """
        if not date_str:
            return None
        
        try:
            from datetime import datetime
            
            # 尝试不同的日期格式
            formats = [
                '%Y-%m-%d',      # 2024-01-01
                '%Y%m%d',        # 20240101
                '%Y/%m/%d',      # 2024/01/01
                '%Y.%m.%d',      # 2024.01.01
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    # 转换为毫秒时间戳
                    return int(dt.timestamp() * 1000)
                except ValueError:
                    continue
            
            # 如果所有格式都失败，返回 None
            logger.warning(f"无法解析日期格式: {date_str}")
            return None
            
        except Exception as e:
            logger.error(f"日期转换失败: {str(e)}")
            return None
