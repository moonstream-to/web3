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
from .routes.dropper import app as dropper_app
from .routes.leaderboard import app as leaderboard_app 
from .routes.admin import app as admin_app
from .routes.play import app as play_app


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tags_metadata = [
    {"name": "drops", "description": 'Api wich servies dropper contracts "./leaderboards/docs"'},
    {
        "name": "leaderboard",
        "description": "Api wich servies moonstream engine"
    },
]


app = FastAPI(
    title=f"Engine HTTP API",
    description="Engine API endpoints.",
    version="v0.0.2",
    openapi_tags=tags_metadata,
    openapi_url="/openapi.json",
    docs_url=None,
)

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


@app.get("/now", tags=["time"])
async def now_handler() -> data.NowResponse:
    """
    Get server current time.
    """
    return data.NowResponse(epoch_time=time.time())


app.mount("/leaderboards", dropper_app)
app.mount("/drops", dropper_app)
app.mount("/admin", admin_app)
app.mount("/play", play_app)
