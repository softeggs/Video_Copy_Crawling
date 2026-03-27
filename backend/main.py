from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, DATABASE_URL, engine
from backend.routers.admin import router as admin_router
from backend.routers.auth import router as auth_router
from backend.routers.videos import router as videos_router
from backend.routers.shortcut_keys import router as shortcut_keys_router, router2 as shortcut_submit_router
from backend.schemas import HealthResponse

app = FastAPI(title="Video Copy Crawling Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(videos_router)
app.include_router(admin_router)
app.include_router(shortcut_keys_router)
app.include_router(shortcut_submit_router)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", database_url=DATABASE_URL, service="video-copy-backend")
