from __future__ import annotations

from urllib.parse import urlparse

from utils.url_cleaner import URLCleaner

INVALID_VIDEO_URL_MESSAGE = "请输入有效的视频链接"


def normalize_video_url(raw_url: str) -> str:
    """统一清洗和标准化用户提交的链接。

    这里不限制具体平台，只保证它是一个可解析、可追踪的 http(s) URL，
    从而拦住 `1`、`2` 这类无效输入。
    """

    if not isinstance(raw_url, str):
        raise ValueError(INVALID_VIDEO_URL_MESSAGE)

    candidate = raw_url.strip()
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
