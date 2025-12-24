import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *
from typing import Dict
from utils.logger import logger
from utils.config import config

class FeishuSync:
    def __init__(self):
        self.client = lark.Client.builder() \
            .app_id(config.FEISHU_APP_ID) \
            .app_secret(config.FEISHU_APP_SECRET) \
            .build()
        
        self.app_token = config.FEISHU_BITABLE_APP_TOKEN
        self.table_id = config.FEISHU_BITABLE_TABLE_ID
    
    async def sync_to_bitable(self, content: Dict, metadata: Dict, markdown_path: str) -> bool:
        """同步到飞书多维表格"""
        try:
            logger.info("开始同步到飞书")
            
            # 构建记录字段
            fields = {
                "标题": content.get('title', ''),
                "原始链接": metadata.get('url', ''),
                "作者": metadata.get('author', ''),
                "发布日期": metadata.get('upload_date', ''),
                "一句话总结": content.get('summary', ''),
                "核心观点": "\n".join(content.get('core_points', [])),
                "详细内容": content.get('detailed_content', ''),
                "金句": "\n".join(content.get('golden_sentences', [])),
                "标签": content.get('tags', []),
                "笔记路径": markdown_path,
                "处理状态": "已完成",
                "处理时间": self._get_current_timestamp()
            }
            
            # 创建记录
            request = CreateAppTableRecordRequest.builder() \
                .app_token(self.app_token) \
                .table_id(self.table_id) \
                .request_body(AppTableRecord.builder()
                    .fields(fields)
                    .build()) \
                .build()
            
            response = self.client.bitable.v1.app_table_record.create(request)
            
            if not response.success():
                logger.error(f"飞书同步失败: {response.code} - {response.msg}")
                return False
            
            logger.info(f"飞书同步成功，记录 ID: {response.data.record.record_id}")
            return True
            
        except Exception as e:
            logger.error(f"飞书同步异常: {str(e)}")
            return False
    
    async def update_record_status(self, record_id: str, status: str, error_msg: str = None):
        """更新记录状态"""
        try:
            fields = {"处理状态": status}
            if error_msg:
                fields["错误信息"] = error_msg
            
            request = UpdateAppTableRecordRequest.builder() \
                .app_token(self.app_token) \
                .table_id(self.table_id) \
                .record_id(record_id) \
                .request_body(AppTableRecord.builder()
                    .fields(fields)
                    .build()) \
                .build()
            
            response = self.client.bitable.v1.app_table_record.update(request)
            return response.success()
            
        except Exception as e:
            logger.error(f"更新记录状态失败: {str(e)}")
            return False
    
    @staticmethod
    def _get_current_timestamp() -> int:
        """获取当前时间戳（毫秒）"""
        import time
        return int(time.time() * 1000)
