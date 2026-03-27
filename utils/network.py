from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

import requests

PROXY_ENV_KEYS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
)


@contextmanager
def disable_proxy_env() -> Generator[None, None, None]:
    """临时移除代理环境变量，避免第三方库继承错误系统代理。"""

    original_values = {key: os.environ.pop(key, None) for key in PROXY_ENV_KEYS}
    try:
        yield
    finally:
        for key, value in original_values.items():
            if value is not None:
                os.environ[key] = value


def create_direct_requests_session() -> requests.Session:
    """创建不继承系统代理的 requests 会话。"""

    session = requests.Session()
    session.trust_env = False
    return session
