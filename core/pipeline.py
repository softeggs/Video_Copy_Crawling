import asyncio
from pathlib import Path
from typing import Dict, Callable
from .downloader import VideoDownloader
from .audio_processor import AudioProcessor
from .transcriber import Transcriber
from .ai_processor import AIProcessor, ProcessedContent
from .feishu_sync import FeishuSync
from utils.logger import logger
from utils.config import config

class ProcessingPipeline:
    """完整的处理流水线"""
    
    def __init__(self, ai_provider: str = None, enable_ai_polish: bool = None, whisper_model: str = None):
        """初始化处理流水线
        
        Args:
            ai_provider: AI 提供商 ('openai' 或 'gemini')
            enable_ai_polish: 是否启用 AI 润色
            whisper_model: Whisper 模型名称 ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.downloader = VideoDownloader()
        self.audio_processor = AudioProcessor()
        
        # 创建 Transcriber 时传入模型名称
        if whisper_model:
            self.transcriber = Transcriber(model_name=whisper_model)
        else:
            self.transcriber = Transcriber()
            
        self.ai_processor = AIProcessor(provider=ai_provider)
        self.feishu_sync = FeishuSync()
        
        # 如果指定了 enable_ai_polish，覆盖配置
        if enable_ai_polish is not None:
            self.ai_processor.enable_polish = enable_ai_polish
    
    async def process(self, url: str, progress_callback: Callable = None, skip_feishu_sync: bool = False) -> Dict:
        """执行完整的处理流程
        
        Args:
            url: 视频链接
            progress_callback: 进度回调函数
            skip_feishu_sync: 是否跳过飞书同步（创建新记录），用于定时任务模式
        """
        try:
            # 1. 下载视频
            self._update_progress(progress_callback, "📥 下载视频中...")
            metadata = await self.downloader.download_with_retry(url, progress_callback)
            
            # 2. 优化音频
            self._update_progress(progress_callback, "🎵 优化音频格式...")
            optimized_audio = self.audio_processor.optimize_for_asr(
                metadata['audio_file']
            )
            
            # 3. 语音识别
            self._update_progress(progress_callback, "🎙️ 语音识别中...")
            transcription = await self.transcriber.transcribe(
                optimized_audio, 
                progress_callback
            )
            
            # 4. AI 处理（如果启用）
            if self.ai_processor.enable_polish:
                self._update_progress(progress_callback, "🤖 AI 分析与润色...")
                try:
                    processed_content = await self.ai_processor.process(
                        transcription['text'],
                        metadata,
                        progress_callback
                    )
                except Exception as ai_error:
                    # AI 处理失败，自动跳过并使用原始文本
                    logger.warning(f"AI 处理失败，跳过 AI 润色: {str(ai_error)}")
                    self._update_progress(progress_callback, "⚠️ AI 处理失败，使用原始文本...")
                    
                    # 使用基础处理（不经过 AI）
                    processed_content = self.ai_processor._create_basic_content(
                        transcription['text'],
                        metadata
                    )
            else:
                self._update_progress(progress_callback, "📝 整理内容...")
                processed_content = await self.ai_processor.process(
                    transcription['text'],
                    metadata,
                    progress_callback
                )
            
            # 5. 生成 Markdown
            self._update_progress(progress_callback, "📝 生成笔记...")
            markdown = self.ai_processor.generate_markdown(
                processed_content,
                metadata
            )
            
            # 保存 Markdown
            output_file = config.OUTPUT_PATH / f"{metadata['video_id']}.md"
            output_file.write_text(markdown, encoding='utf-8')
            logger.info(f"笔记已保存: {output_file}")
            
            # 6. 同步到飞书（仅在非定时任务模式下创建新记录）
            sync_success = False
            if not skip_feishu_sync:
                self._update_progress(progress_callback, "☁️ 同步到飞书...")
                sync_success = await self.feishu_sync.sync_to_bitable(
                    processed_content.dict(),
                    metadata,
                    str(output_file)
                )
            else:
                logger.info("跳过飞书同步（定时任务模式，将由调度器更新记录）")
            
            # 7. 清理临时文件（保留原始下载文件，只删除优化后的临时文件）
            # 只删除 _optimized.wav 文件，保留原始下载的音频
            if optimized_audio != metadata['audio_file']:
                self._cleanup_temp_files(optimized_audio)
                logger.info(f"已保留原始文件: {metadata['audio_file']}")
            
            self._update_progress(progress_callback, "✅ 处理完成！")
            
            return {
                'success': True,
                'metadata': metadata,
                'transcription': transcription['text'],
                'processed_content': processed_content.dict(),
                'markdown_path': str(output_file),
                'feishu_synced': sync_success
            }
            
        except Exception as e:
            logger.error(f"处理流程失败: {str(e)}")
            self._update_progress(progress_callback, f"❌ 错误: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def process_batch(self, urls: list, progress_callback: Callable = None) -> list:
        """批量处理多个链接"""
        tasks = [self.process(url, progress_callback) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    @staticmethod
    def _update_progress(callback: Callable, message: str):
        """更新进度"""
        if callback:
            callback(message)
        logger.info(message)
    
    @staticmethod
    def _cleanup_temp_files(*files):
        """清理临时文件"""
        for file in files:
            try:
                Path(file).unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"清理文件失败 {file}: {str(e)}")
