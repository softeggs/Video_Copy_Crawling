import ffmpeg
from pathlib import Path
from utils.logger import logger

class AudioProcessor:
    @staticmethod
    def optimize_for_asr(input_file: str, output_file: str = None) -> str:
        """优化音频文件用于 ASR 识别
        
        转换为 16kHz 单声道 WAV 格式
        """
        try:
            input_path = Path(input_file)
            
            if output_file is None:
                output_file = str(input_path.parent / f"{input_path.stem}_optimized.wav")
            
            logger.info(f"开始优化音频: {input_file}")
            
            # FFmpeg 处理
            stream = ffmpeg.input(input_file)
            stream = ffmpeg.output(
                stream,
                output_file,
                acodec='pcm_s16le',  # 16-bit PCM
                ac=1,                 # 单声道
                ar='16000'            # 16kHz 采样率
            )
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            logger.info(f"音频优化完成: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"音频处理失败: {str(e)}")
            raise
    
    @staticmethod
    def get_audio_duration(file_path: str) -> float:
        """获取音频时长（秒）"""
        try:
            probe = ffmpeg.probe(file_path)
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            logger.error(f"获取音频时长失败: {str(e)}")
            return 0.0
