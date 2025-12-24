"""
平台检测和管理模块
"""
from enum import Enum
from typing import Optional
from pathlib import Path

class Platform(Enum):
    """支持的平台"""
    BILIBILI = "bilibili"
    XIAOHONGSHU = "xiaohongshu"
    DOUYIN = "douyin"
    UNKNOWN = "unknown"

class PlatformDetector:
    """平台检测器"""
    
    # 平台域名映射
    PLATFORM_DOMAINS = {
        Platform.BILIBILI: [
            'bilibili.com',
            'b23.tv',
            'acg.tv'
        ],
        Platform.XIAOHONGSHU: [
            'xiaohongshu.com',
            'xhslink.com',
            'xhs.cn'
        ],
        Platform.DOUYIN: [
            'douyin.com',
            'iesdouyin.com',
            'v.douyin.com'
        ]
    }
    
    # 平台显示名称
    PLATFORM_NAMES = {
        Platform.BILIBILI: "B站",
        Platform.XIAOHONGSHU: "小红书",
        Platform.DOUYIN: "抖音",
        Platform.UNKNOWN: "未知平台"
    }
    
    # 平台 Cookies 文件名
    PLATFORM_COOKIES = {
        Platform.BILIBILI: "cookies_bilibili.txt",
        Platform.XIAOHONGSHU: "cookies_xiaohongshu.txt",
        Platform.DOUYIN: "cookies_douyin.txt"
    }
    
    # 平台 Referer
    PLATFORM_REFERERS = {
        Platform.BILIBILI: "https://www.bilibili.com/",
        Platform.XIAOHONGSHU: "https://www.xiaohongshu.com/",
        Platform.DOUYIN: "https://www.douyin.com/"
    }
    
    @classmethod
    def detect_platform(cls, url: str) -> Platform:
        """
        检测 URL 所属平台
        
        Args:
            url: 视频链接
            
        Returns:
            Platform: 平台枚举
        """
        url_lower = url.lower()
        
        for platform, domains in cls.PLATFORM_DOMAINS.items():
            for domain in domains:
                if domain in url_lower:
                    return platform
        
        return Platform.UNKNOWN
    
    @classmethod
    def get_platform_name(cls, platform: Platform) -> str:
        """获取平台显示名称"""
        return cls.PLATFORM_NAMES.get(platform, "未知平台")
    
    @classmethod
    def get_cookies_file(cls, platform: Platform) -> Optional[str]:
        """获取平台对应的 cookies 文件路径"""
        if platform == Platform.UNKNOWN:
            return None
        return cls.PLATFORM_COOKIES.get(platform)
    
    @classmethod
    def get_referer(cls, platform: Platform) -> str:
        """获取平台对应的 Referer"""
        return cls.PLATFORM_REFERERS.get(platform, "https://www.bilibili.com/")
    
    @classmethod
    def is_supported(cls, platform: Platform) -> bool:
        """检查平台是否支持"""
        return platform != Platform.UNKNOWN
    
    @classmethod
    def get_all_platforms(cls) -> list:
        """获取所有支持的平台"""
        return [p for p in Platform if p != Platform.UNKNOWN]
    
    @classmethod
    def check_cookies_exists(cls, platform: Platform) -> bool:
        """检查平台 cookies 文件是否存在"""
        cookies_file = cls.get_cookies_file(platform)
        if not cookies_file:
            return False
        return Path(cookies_file).exists()
