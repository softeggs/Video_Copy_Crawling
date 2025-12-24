"""
抖音视频下载辅助工具
使用第三方 API 服务下载抖音视频
"""
import requests
import re
from pathlib import Path
from typing import Dict, Optional
from utils.logger import logger

class DouyinDownloader:
    """抖音视频下载器（使用第三方 API）"""
    
    # SaveTik API 端点
    SAVETIK_API = "https://savetik.co/api/ajaxSearch"
    
    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        """
        从抖音 URL 中提取视频 ID
        
        Args:
            url: 抖音视频链接
            
        Returns:
            视频 ID 或 None
        """
        # 匹配视频 ID
        patterns = [
            r'/video/(\d+)',
            r'modal_id=(\d+)',
            r'v\.douyin\.com/([A-Za-z0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    @classmethod
    def get_download_url(cls, video_url: str) -> Dict:
        """
        通过 SaveTik 网站获取下载链接
        
        Args:
            video_url: 抖音视频链接
            
        Returns:
            包含下载信息的字典
        """
        try:
            logger.info(f"正在通过 SaveTik 获取下载链接: {video_url}")
            
            # 准备请求头（根据实际浏览器请求）
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://savetik.io',
                'Referer': 'https://savetik.io/zh-cn/douyin-video-downloader',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
            }
            
            # 准备表单数据
            data = {
                'q': video_url,
                'lang': 'zh-cn'
            }
            
            # 发送请求到 SaveTik
            response = requests.post(
                "https://savetik.io/api/ajaxSearch",
                headers=headers,
                data=data,
                timeout=30
            )
            
            response.raise_for_status()
            
            # 响应内容（requests 会自动解压缩）
            content = response.text
            
            # 尝试解析 JSON
            try:
                result = response.json()
            except ValueError:
                # 如果不是 JSON，记录错误
                logger.error(f"响应不是 JSON 格式，前200字符: {content[:200]}")
                return {
                    'success': False,
                    'error': 'SaveTik 返回格式错误，可能服务不可用'
                }
            
            logger.info("成功获取 SaveTik 响应")
            logger.debug(f"响应状态: {result.get('status')}")
            
            # 解析响应
            if result.get('status') == 'ok':
                html_content = result.get('data', '')
                
                if isinstance(html_content, str) and html_content:
                    # 使用正则表达式提取下载链接和标题
                    import re
                    
                    # 提取标题
                    title_match = re.search(r'<h3>([^<]+)</h3>', html_content)
                    title = title_match.group(1).strip() if title_match else '未知标题'
                    
                    # 提取下载链接（优先 HD 版本）
                    download_patterns = [
                        r'href="([^"]+)"[^>]*>.*?下载 MP4 HD',  # HD 版本
                        r'href="([^"]+)"[^>]*>.*?下载 MP4',     # 普通版本
                    ]
                    
                    download_url = None
                    for pattern in download_patterns:
                        matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
                        if matches:
                            download_url = matches[0]
                            break
                    
                    # 提取缩略图
                    thumbnail_match = re.search(r'<img src="([^"]+)"', html_content)
                    thumbnail = thumbnail_match.group(1) if thumbnail_match else None
                    
                    if download_url:
                        logger.info(f"成功提取下载链接")
                        logger.info(f"视频标题: {title}")
                        return {
                            'success': True,
                            'data': html_content,
                            'title': title,
                            'download_url': download_url,
                            'thumbnail': thumbnail,
                        }
                    else:
                        logger.warning("未能从响应中提取下载链接")
                        logger.debug(f"HTML 内容前500字符: {html_content[:500]}")
                        return {
                            'success': False,
                            'error': '无法从响应中提取下载链接'
                        }
                else:
                    logger.error("响应数据为空或格式错误")
                    return {
                        'success': False,
                        'error': '响应数据为空'
                    }
            else:
                error_msg = result.get('message', '未知错误')
                logger.error(f"SaveTik 返回错误: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }
        
        except requests.RequestException as e:
            logger.error(f"SaveTik 请求失败: {str(e)}")
            return {
                'success': False,
                'error': f"请求失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"解析 SaveTik 响应失败: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'success': False,
                'error': f"解析失败: {str(e)}"
            }
    
    @classmethod
    def _extract_title(cls, result: dict) -> str:
        """从 API 响应中提取标题"""
        try:
            data = result.get('data', {})
            # 尝试多种可能的字段
            title = (
                data.get('title') or
                data.get('desc') or
                data.get('description') or
                '未知标题'
            )
            return title.strip()
        except:
            return '未知标题'
    
    @classmethod
    def _extract_download_url(cls, result: dict) -> Optional[str]:
        """从 API 响应中提取下载链接"""
        try:
            data = result.get('data', {})
            
            # 尝试多种可能的字段
            download_url = (
                data.get('hdplay') or  # 高清
                data.get('play') or     # 标清
                data.get('wmplay') or   # 带水印
                data.get('url')
            )
            
            return download_url
        except:
            return None
    
    @classmethod
    def _extract_thumbnail(cls, result: dict) -> Optional[str]:
        """从 API 响应中提取缩略图"""
        try:
            data = result.get('data', {})
            return data.get('cover') or data.get('origin_cover')
        except:
            return None
    
    @classmethod
    def download_video(cls, video_url: str, save_path: Path, progress_callback=None) -> Dict:
        """
        下载抖音视频
        
        Args:
            video_url: 抖音视频链接
            save_path: 保存路径
            progress_callback: 进度回调函数
            
        Returns:
            下载结果字典
        """
        try:
            # 获取下载链接
            if progress_callback:
                try:
                    progress_callback("正在获取下载链接...")
                except:
                    pass  # 忽略 Streamlit 上下文错误
            
            api_result = cls.get_download_url(video_url)
            
            if not api_result['success']:
                return api_result
            
            download_url = api_result['download_url']
            if not download_url:
                return {
                    'success': False,
                    'error': '无法获取下载链接'
                }
            
            logger.info(f"开始下载视频: {download_url}")
            
            # 下载视频
            if progress_callback:
                try:
                    progress_callback("正在下载视频...")
                except:
                    pass
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.douyin.com/',
            }
            
            response = requests.get(download_url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()
            
            # 保存文件
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            try:
                                percent = (downloaded / total_size) * 100
                                progress_callback(f"下载中: {percent:.1f}%")
                            except:
                                pass  # 忽略进度回调错误
            
            logger.info(f"视频下载完成: {save_path}")
            
            if progress_callback:
                try:
                    progress_callback("下载完成")
                except:
                    pass
            
            return {
                'success': True,
                'file_path': str(save_path),
                'title': api_result['title'],
                'thumbnail': api_result.get('thumbnail'),
                'size': save_path.stat().st_size
            }
        
        except requests.RequestException as e:
            logger.error(f"下载视频失败: {str(e)}")
            return {
                'success': False,
                'error': f"下载失败: {str(e)}"
            }
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            logger.error(f"下载过程出错: {str(e)}")
            logger.error(f"详细错误: {error_detail}")
            return {
                'success': False,
                'error': f"下载出错: {str(e) or type(e).__name__}"
            }
    
    @classmethod
    def test_api(cls, video_url: str) -> bool:
        """
        测试 API 是否可用
        
        Args:
            video_url: 测试用的视频链接
            
        Returns:
            API 是否可用
        """
        try:
            result = cls.get_download_url(video_url)
            return result['success']
        except:
            return False
