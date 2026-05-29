from __future__ import annotations

import re
from urllib.parse import urlparse

from utils.url_cleaner import URLCleaner

INVALID_VIDEO_URL_MESSAGE = "请输入有效的视频链接"
URL_IN_TEXT_PATTERN = re.compile(r"https?://[^\s<>\"'`]+", re.IGNORECASE)
TRAILING_NOISE_CHARS = ".,;!?)>]}\"'，。；！？】）"


def _strip_embedded_noise(candidate: str) -> str:
    """裁掉快捷指令分享文本里拼进 URL 的明显噪声尾巴。"""

    cleaned_candidate = candidate.strip().rstrip(TRAILING_NOISE_CHARS)
    lowered = cleaned_candidate.lower()
    for marker in ("/mailto:", "mailto:"):
        marker_index = lowered.find(marker)
        if marker_index != -1:
            suffix_start = marker_index + 1 if marker.startswith("/") else marker_index
            return cleaned_candidate[:suffix_start].rstrip(TRAILING_NOISE_CHARS)
    return cleaned_candidate


def _extract_url_candidate(raw_url: str) -> str:
    """从整段分享文案中提取首个 URL 候选。"""

    stripped = raw_url.strip()
    matched = URL_IN_TEXT_PATTERN.search(stripped)
    if matched:
        return _strip_embedded_noise(matched.group(0))
    return _strip_embedded_noise(stripped)


def normalize_video_url(raw_url: str) -> str:
    """统一清洗和标准化用户提交的链接。

    这里不限制具体平台，只保证它是一个可解析、可追踪的 http(s) URL，
    从而拦住 `1`、`2` 这类无效输入。
    """

    if not isinstance(raw_url, str):
        raise ValueError(INVALID_VIDEO_URL_MESSAGE)

    candidate = _extract_url_candidate(raw_url)
    if not candidate:
        raise ValueError(INVALID_VIDEO_URL_MESSAGE)

    if candidate.startswith("#"):
        raise ValueError(INVALID_VIDEO_URL_MESSAGE)

    lowered = candidate.lower()
    if "netscape http cookie" in lowered or "cookie_spec" in lowered:
        raise ValueError(INVALID_VIDEO_URL_MESSAGE)

    if not candidate.startswith(("http://", "https://")):
        if " " in candidate or "." not in candidate:
            raise ValueError(INVALID_VIDEO_URL_MESSAGE)
        candidate = f"https://{candidate}"

    cleaned = URLCleaner.clean_url(candidate)
    parsed = urlparse(cleaned)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError(INVALID_VIDEO_URL_MESSAGE)

    if not parsed.netloc or "." not in parsed.netloc:
        raise ValueError(INVALID_VIDEO_URL_MESSAGE)

    if parsed.path in {"", "/"} and not parsed.query:
        raise ValueError(INVALID_VIDEO_URL_MESSAGE)

    return cleaned
