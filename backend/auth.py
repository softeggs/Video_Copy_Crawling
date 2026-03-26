from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from utils.config import config


def hash_password(password: str) -> str:
    """使用标准库实现 PBKDF2 密码摘要，避免额外依赖。"""

    iterations = 600_000
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations).hex()
    return f"pbkdf2_sha256${iterations}${salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    """校验密码摘要。"""

    try:
        scheme, raw_iterations, salt, digest = stored_hash.split("$", 3)
    except ValueError:
        return False

    if scheme != "pbkdf2_sha256":
        return False

    candidate = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(raw_iterations),
    ).hex()
    return hmac.compare_digest(candidate, digest)


def create_access_token(user_id: int, expires_delta: timedelta | None = None) -> str:
    """创建访问令牌。"""

    expire_at = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=config.JWT_EXPIRE_MINUTES))
    payload: dict[str, Any] = {"sub": str(user_id), "exp": expire_at}
    return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """解析访问令牌，失败返回 None。"""

    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None

    raw_user_id = payload.get("sub")
    if raw_user_id is None:
        return None

    try:
        return int(raw_user_id)
    except (TypeError, ValueError):
        return None


def encode_debug_value(value: str) -> str:
    """为调试台准备可读但安全的摘要。"""

    return base64.urlsafe_b64encode(value.encode("utf-8")).decode("ascii")

