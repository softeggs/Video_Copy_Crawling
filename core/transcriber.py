import whisper
import asyncio
from pathlib import Path
from typing import Dict
from utils.logger import logger
from utils.config import config

class Transcriber:
    def __init__(self, model_name: str = None):
        """初始化转录器
        
        Args:
            model_name: Whisper 模型名称，如果为 None 则使用配置文件中的值
        """
        self.model_name = model_name or config.WHISPER_MODEL
        self.model = None
    
    def load_model(self):
        """延迟加载模型"""
        if self.model is None:
            logger.info(f"加载 Whisper 模型: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            logger.info("模型加载完成")
    
    async def transcribe(self, audio_file: str, progress_callback=None) -> Dict:
        """转录音频文件"""
        try:
            self.load_model()
            
            if progress_callback:
                progress_callback("正在识别语音...")
            
            logger.info(f"开始转录: {audio_file}")
            
            # 异步执行转录
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._transcribe_sync,
                audio_file
            )
            
            logger.info(f"转录完成，识别文本长度: {len(result['text'])} 字符")
            
            if progress_callback:
                progress_callback("语音识别完成")
            
            return result
            
        except Exception as e:
            logger.error(f"转录失败: {str(e)}")
            raise
    
    def _transcribe_sync(self, audio_file: str) -> Dict:
        """同步转录方法"""
        result = self.model.transcribe(
            audio_file,
            language='zh',  # 中文
            task='transcribe',
            verbose=False,
            # 优化参数以提高识别准确度
            temperature=0.0,  # 降低随机性，提高稳定性
            best_of=5,  # 尝试多次采样，选择最佳结果
            beam_size=5,  # 使用束搜索提高准确度
            patience=1.0,  # 束搜索的耐心参数
            compression_ratio_threshold=2.4,  # 压缩率阈值
            logprob_threshold=-1.0,  # 对数概率阈值
            no_speech_threshold=0.6,  # 无语音阈值
            condition_on_previous_text=True,  # 基于前文进行条件预测
            initial_prompt="这是一段中文视频的语音内容，可能包含网络用语、口语化表达。",  # 提示词
        )
        
        return {
            'text': result['text'].strip(),
            'segments': result.get('segments', []),
            'language': result.get('language', 'zh')
        }
    
    def get_segments_with_timestamps(self, segments: list) -> str:
        """获取带时间戳的文本"""
        formatted = []
        for seg in segments:
            start = self._format_timestamp(seg['start'])
            end = self._format_timestamp(seg['end'])
            text = seg['text'].strip()
            formatted.append(f"[{start} -> {end}] {text}")
        return "\n".join(formatted)
    
    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """格式化时间戳"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
