"""Check DB state and fix Alembic version."""
from backend.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
    print("Tables:", [t[0] for t in tables])
    try:
        versions = conn.execute(text("SELECT * FROM alembic_version")).fetchall()
        print("Alembic versions:", versions)
    except Exception as e:
        print("alembic_version error:", e)

    # Check videos table columns
    cols = conn.execute(text("PRAGMA table_info(videos)")).fetchall()
    print("videos columns:", [c[1] for c in cols])
