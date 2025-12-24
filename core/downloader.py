import asyncio
import yt_dlp
import requests
import subprocess
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse
from utils.logger import logger
from utils.config import config
from utils.platform_detector import PlatformDetector, Platform
from utils.douyin_helper import DouyinDownloader

class VideoDownloader:
    def __init__(self, cookies_file: str = None):
        self.download_path = config.DOWNLOAD_PATH
        self.cookies_file = cookies_file or config.COOKIES_FILE
        self.platform_detector = PlatformDetector()
        
    async def download(self, url: str, progress_callback=None) -> Dict:
        """下载视频并提取元数据"""
        try:
            # 确保 URL 有协议前缀
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # 检测平台
            platform = self.platform_detector.detect_platform(url)
            platform_name = self.platform_detector.get_platform_name(platform)
            
            logger.info(f"开始下载视频: {url}")
            logger.info(f"检测到平台: {platform_name}")
            
            # 检查平台是否支持
            if not self.platform_detector.is_supported(platform):
                error_msg = f"该平台暂不支持: {platform_name}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # 特殊处理：抖音使用第三方 API
            if platform == Platform.DOUYIN:
                logger.info("检测到抖音平台，使用第三方 API 下载")
                return await self._download_douyin(url, progress_callback)
            
            # 其他平台使用 yt-dlp
            return await self._download_with_ytdlp(url, platform, platform_name, progress_callback)
            
        except Exception as e:
            logger.error(f"下载失败: {str(e)}")
            raise
    
    async def _download_douyin(self, url: str, progress_callback=None) -> Dict:
        """
        使用第三方 API 下载抖音视频
        
        Args:
            url: 抖音视频链接
            progress_callback: 进度回调
            
        Returns:
            下载结果字典
        """
        try:
            if progress_callback:
                progress_callback("正在通过第三方 API 获取下载链接...")
            
            # 使用 DouyinDownloader 获取下载链接并下载
            loop = asyncio.get_event_loop()
            
            # 生成保存路径
            video_id = DouyinDownloader.extract_video_id(url) or 'douyin_video'
            save_path = self.download_path / f"{video_id}.mp4"
            
            # 异步执行下载
            result = await loop.run_in_executor(
                None,
                DouyinDownloader.download_video,
                url,
                save_path,
                progress_callback
            )
            
            if not result['success']:
                raise Exception(result.get('error', '下载失败'))
            
            # 转换为统一的返回格式
            video_path = Path(result['file_path'])
            
            # 提取音频
            if progress_callback:
                progress_callback("正在提取音频...")
            
            audio_file = await self._extract_audio_from_video(video_path)
            
            return {
                'video_id': video_id,
                'title': result.get('title', '未知标题'),
                'author': '抖音用户',
                'upload_date': '',
                'description': '',
                'tags': [],
                'thumbnail': result.get('thumbnail', ''),
                'audio_file': str(audio_file),
                'url': url,
                'video_file': str(video_path)
            }
            
        except Exception as e:
            logger.error(f"抖音视频下载失败: {str(e)}")
            raise Exception(f"抖音下载失败: {str(e)}")
    
    async def _extract_audio_from_video(self, video_path: Path) -> Path:
        """
        从视频文件中提取音频
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            音频文件路径
        """
        try:
            audio_path = video_path.with_suffix('.wav')
            
            # 使用 ffmpeg 提取音频
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-vn',  # 不处理视频
                '-acodec', 'pcm_s16le',  # WAV 格式
                '-ar', '16000',  # 采样率
                '-ac', '1',  # 单声道
                '-y',  # 覆盖已存在的文件
                str(audio_path)
            ]
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: subprocess.run(cmd, capture_output=True, check=True)
            )
            
            logger.info(f"音频提取成功: {audio_path}")
            return audio_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"音频提取失败: {e.stderr.decode() if e.stderr else str(e)}")
            raise Exception("音频提取失败，请确保已安装 ffmpeg")
        except Exception as e:
            logger.error(f"音频提取出错: {str(e)}")
            raise
    
    async def _download_with_ytdlp(self, url: str, platform: Platform, platform_name: str, progress_callback=None) -> Dict:
        """
        使用 yt-dlp 下载视频（B站、小红书等）
        
        Args:
            url: 视频链接
            platform: 平台枚举
            platform_name: 平台名称
            progress_callback: 进度回调
            
        Returns:
            下载结果字典
        """
        try:
            # 获取平台对应的 cookies 文件
            platform_cookies = self.platform_detector.get_cookies_file(platform)
            cookies_to_use = None
            
            if platform_cookies and Path(platform_cookies).exists():
                cookies_to_use = platform_cookies
                logger.info(f"使用 {platform_name} cookies: {platform_cookies}")
            elif self.cookies_file and Path(self.cookies_file).exists():
                # 回退到通用 cookies 文件
                cookies_to_use = self.cookies_file
                logger.info(f"使用通用 cookies: {self.cookies_file}")
            else:
                logger.warning(f"未找到 {platform_name} 的 cookies 文件")
            
            # 获取平台对应的 Referer
            referer = self.platform_detector.get_referer(platform)
            
            # 基础配置
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(self.download_path / '%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }],
                # 添加更好的请求头
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate',
                    'Referer': referer,
                },
                # 忽略错误继续
                'ignoreerrors': False,
                # 重试次数
                'retries': 5,
                # 片段重试
                'fragment_retries': 5,
                # 跳过不可用的片段
                'skip_unavailable_fragments': True,
            }
            
            # 如果有 cookies 文件，使用它
            if cookies_to_use:
                ydl_opts['cookiefile'] = cookies_to_use
            
            if progress_callback:
                def hook(d):
                    try:
                        if d['status'] == 'downloading':
                            progress = d.get('_percent_str', '0%')
                            progress_callback(f"下载中: {progress}")
                        elif d['status'] == 'finished':
                            progress_callback("下载完成，正在转换格式...")
                    except Exception as e:
                        # 忽略 progress callback 的错误（如 NoSessionContext）
                        logger.debug(f"Progress callback 错误（已忽略）: {str(e)}")
                
                ydl_opts['progress_hooks'] = [hook]
            
            # 异步执行下载
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._download_sync, 
                url, 
                ydl_opts
            )
            
            logger.info(f"视频下载成功: {result['title']}")
            return result
            
        except Exception as e:
            logger.error(f"yt-dlp 下载失败: {str(e)}")
            raise
    
    def _download_sync(self, url: str, ydl_opts: dict) -> Dict:
        """同步下载方法"""
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if not info:
                    raise Exception("无法获取视频信息")
                
                # 提取元数据
                video_id = info.get('id', 'unknown')
                
                # 检查音频文件是否存在
                # yt-dlp 可能生成不同的扩展名
                possible_extensions = ['wav', 'm4a', 'mp3', 'webm', 'opus']
                audio_file = None
                
                for ext in possible_extensions:
                    test_file = self.download_path / f"{video_id}.{ext}"
                    if test_file.exists():
                        audio_file = test_file
                        break
                
                if not audio_file:
                    # 如果没有找到，使用默认的 wav
                    audio_file = self.download_path / f"{video_id}.wav"
                
                return {
                    'video_id': video_id,
                    'title': info.get('title', '未知标题'),
                    'author': info.get('uploader', '未知作者'),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', ''),
                    'tags': info.get('tags', []),
                    'thumbnail': info.get('thumbnail', ''),
                    'audio_file': str(audio_file),
                    'url': url
                }
        except Exception as e:
            # 记录详细错误信息
            error_msg = f"下载失败: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
    
    async def download_with_retry(self, url: str, progress_callback=None) -> Optional[Dict]:
        """带重试机制的下载"""
        for attempt in range(config.MAX_RETRIES):
            try:
                return await self.download(url, progress_callback)
            except Exception as e:
                logger.warning(f"下载尝试 {attempt + 1}/{config.MAX_RETRIES} 失败: {str(e)}")
                if attempt == config.MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # 指数退避
        return None
