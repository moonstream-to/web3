"""
Moonstream Engine Admin API.
"""
import logging
import time
from typing import Dict


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .. import data
from ..middleware import DropperHTTPException, DropperAuthMiddleware
from ..settings import (
    DOCS_TARGET_PATH,
    ORIGINS,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tags_metadata = [{"name": "admin", "description": "Moonstream Engine Admin API"}]


app = FastAPI(
    title=f"Moonstream Engine Admin API",
    description="Moonstream Engine Admin API endpoints.",
    version="v0.0.1",
    openapi_tags=tags_metadata,
    openapi_url="/openapi.json",
    docs_url=None,
    redoc_url=f"/{DOCS_TARGET_PATH}",
)


app.add_middleware(DropperAuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping", response_model=data.PingResponse)
async def ping_handler() -> data.PingResponse:
    """
    Check server status.
    """
    return data.PingResponse(status="ok")
