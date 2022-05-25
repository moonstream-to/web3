"""
Lootbox API.
"""
import logging
import time
from typing import Dict

from brownie import network


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import data
from .middleware import DropperHTTPException, DropperAuthMiddleware
from .settings import (
    ENGINE_BROWNIE_NETWORK,
    DOCS_TARGET_PATH,
    ORIGINS,
)
from .routes.dropper import router as dropper_router
from .routes.leaderboard import router as leaderboard_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tags_metadata = [
    {"name": "drops", "description": "Api wich servies dropper contracts"},
    {
        "name": "leaderboard",
        "description": "Api wich servies leaderboards",
    },
]


app = FastAPI(
    title=f"Engine HTTP API",
    description="Engine API endpoints.",
    version="v0.0.2",
    openapi_tags=tags_metadata,
    openapi_url="/openapi.json",
    docs_url=None,
    redoc_url=f"/{DOCS_TARGET_PATH}",
)


whitelist_paths: Dict[str, str] = {}
whitelist_paths.update(
    {
        "/ping": "GET",
        "/docs": "GET",
        "/drops": "GET",
        "/drops/batch": "GET",
        "/drops/claims": "GET",
        "/drops/contracts": "GET",
        "/drops/terminus": "GET",
        "/drops/blockchains": "GET",
        "/drops/terminus/claims": "GET",
        "/leaderboard/count/addresses": "GET",
        "/leaderboard/quartiles": "GET",
        "/leaderboard/position": "GET",
        "/leaderboard/status": "GET",
        "/leaderboard": "GET",
        "/now": "GET",
        "/status": "GET",
        "/openapi.json": "GET",
    }
)

app.add_middleware(DropperAuthMiddleware, whitelist=whitelist_paths)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping", response_model=data.PingResponse, tags=["status"])
async def ping_handler() -> data.PingResponse:
    """
    Check server status.
    """
    return data.PingResponse(status="ok")


@app.get("/now", tags=["time"])
async def now_handler() -> data.NowResponse:
    """
    Get server current time.
    """
    return data.NowResponse(epoch_time=time.time())


app.include_router(leaderboard_router)
app.include_router(dropper_router)
