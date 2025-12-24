"""
URL 清理工具
自动移除 URL 中的 cookies 和敏感参数
"""
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import re

class URLCleaner:
    """URL 清理器"""
    
    # 需要移除的参数（只移除明确的安全敏感信息）
    SENSITIVE_PARAMS = [
        # 明确的 cookies 和 token
        'cookie',
        'cookies',
        'session',
        'sessdata',  # B站
        'token',
        'access_token',
        'auth_token',
        'xsec_token',  # 小红书安全 token
        'auth',
        'key',
        'secret',
        'api_key',
        # 用户标识（可能泄露隐私）
        'uid',
        'user_id',
        'openid',
        # 设备标识
        'device_id',
        'imei',
        'mac',
    ]
    
    # 可选移除的追踪参数（不影响视频访问）
    TRACKING_PARAMS = [
        # 分享追踪
        'share_source',
        'share_medium',
        'share_session_id',
        'share_id',
        'share_tag',
        # 来源追踪
        'from_source',
        'from_spmid',
        'spm_id_from',
        'enter_from',
        'enter_method',
        'previous_page',
        # 其他追踪
        'utm_source',
        'utm_medium',
        'utm_campaign',
    ]
    
    @classmethod
    def clean_url(cls, url: str, platform: str = None, aggressive: bool = False) -> str:
        """
        清理 URL，移除 cookies 和敏感参数
        
        Args:
            url: 原始 URL
            platform: 平台名称（bilibili/xiaohongshu/douyin）
            aggressive: 是否激进清理（移除追踪参数），默认 False 只移除敏感信息
            
        Returns:
            清理后的 URL
        """
        if not url or not isinstance(url, str):
            return url
        
        # 移除首尾空格
        url = url.strip()
        
        # 检查是否是有效的 URL
        if not url.startswith(('http://', 'https://', 'www.')):
            # 如果没有协议，添加 https://
            if not url.startswith('#'):
                url = 'https://' + url
            else:
                return url
        
        try:
            # 解析 URL
            parsed = urlparse(url)
            
            # 获取查询参数
            params = parse_qs(parsed.query, keep_blank_values=True)
            
            # 确定要移除的参数列表
            remove_params = set(cls.SENSITIVE_PARAMS)
            
            # 如果是激进模式，也移除追踪参数
            if aggressive:
                remove_params.update(cls.TRACKING_PARAMS)
            
            # 过滤参数（只移除敏感参数）
            cleaned_params = {}
            for key, value in params.items():
                # 检查参数名是否需要移除
                if key.lower() not in remove_params:
                    cleaned_params[key] = value
            
            # 重建查询字符串
            if cleaned_params:
                # 将列表值转换为单个值
                query_dict = {k: v[0] if isinstance(v, list) and len(v) == 1 else v 
                             for k, v in cleaned_params.items()}
                new_query = urlencode(query_dict, doseq=True)
            else:
                new_query = ''
            
            # 重建 URL
            cleaned_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                ''  # 移除 fragment
            ))
            
            return cleaned_url
            
        except Exception as e:
            # 如果解析失败，返回原始 URL
            return url
    
    @classmethod
    def extract_video_id(cls, url: str, platform: str = None) -> str:
        """
        从 URL 中提取视频 ID
        
        Args:
            url: 视频 URL
            platform: 平台名称
            
        Returns:
            视频 ID
        """
        try:
            parsed = urlparse(url)
            path = parsed.path
            
            # B站
            if 'bilibili' in parsed.netloc or 'b23.tv' in parsed.netloc:
                # 匹配 BV 号
                match = re.search(r'(BV[a-zA-Z0-9]+)', url)
                if match:
                    return match.group(1)
                # 匹配 av 号
                match = re.search(r'av(\d+)', url)
                if match:
                    return f"av{match.group(1)}"
            
            # 小红书
            elif 'xiaohongshu' in parsed.netloc:
                # 匹配视频 ID
                match = re.search(r'/explore/([a-zA-Z0-9]+)', path)
                if match:
                    return match.group(1)
                match = re.search(r'/item/([a-zA-Z0-9]+)', path)
                if match:
                    return match.group(1)
            
            # 抖音
            elif 'douyin' in parsed.netloc:
                # 匹配视频 ID
                match = re.search(r'/video/(\d+)', path)
                if match:
                    return match.group(1)
            
            return ''
            
        except Exception:
            return ''
    
    @classmethod
    def is_valid_video_url(cls, url: str) -> bool:
        """
        检查是否是有效的视频 URL
        
        Args:
            url: URL 字符串
            
        Returns:
            是否有效
        """
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        
        # 检查是否以 # 开头（可能是 cookies）
        if url.startswith('#'):
            return False
        
        # 检查是否包含 cookies 关键词
        if 'Netscape HTTP Cookie' in url or 'cookie_spec' in url:
            return False
        
        # 检查是否是有效的 URL 格式
        if not url.startswith(('http://', 'https://', 'www.', 'bilibili', 'xiaohongshu', 'douyin', 'b23.tv')):
            return False
        
        # 检查是否包含支持的域名
        supported_domains = [
            'bilibili.com',
            'b23.tv',
            'xiaohongshu.com',
            'xhslink.com',
            'douyin.com',
            'iesdouyin.com',
        ]
        
        url_lower = url.lower()
        return any(domain in url_lower for domain in supported_domains)
