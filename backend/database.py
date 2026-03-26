from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from utils.config import config


def _normalise_sqlite_url(database_url: str) -> str:
    """兼容本地路径和 SQLite URL。"""

    if database_url.startswith("sqlite:///"):
        return database_url
    path = Path(database_url).expanduser().resolve()
    return f"sqlite:///{path.as_posix()}"


DATABASE_URL = (
    _normalise_sqlite_url(config.DATABASE_URL)
    if config.DATABASE_URL.startswith("sqlite") or "://" not in config.DATABASE_URL
    else config.DATABASE_URL
)

engine_kwargs: dict[str, object] = {"future": True, "pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)


class Base(DeclarativeBase):
    """SQLAlchemy 基类。"""


def get_db() -> Generator[Session, None, None]:
    """FastAPI 数据库依赖。"""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

