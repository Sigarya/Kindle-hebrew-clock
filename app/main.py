from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from loguru import logger

from app.api.v1.router import router
from app.core.config import settings
from app.services.clock import log_available_fonts


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(timeout=10.0)
    log_available_fonts()
    logger.info("hebclk starting on port {}", settings.port)
    yield
    await app.state.http_client.aclose()


app = FastAPI(
    title="Hebrew Clock",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
async def health() -> PlainTextResponse:
    return PlainTextResponse("OK")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=False)
