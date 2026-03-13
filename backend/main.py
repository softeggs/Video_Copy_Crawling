from fastapi import FastAPI

from .database import Base, engine
from .routers import admin, auth, videos


app = FastAPI(title="Video Copy Crawling API", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(videos.router)
app.include_router(admin.router)
