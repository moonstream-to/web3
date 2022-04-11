"""
Lootbox API.
"""
import logging
from typing import Dict

from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import data
from .middleware import BroodAuthMiddleware
from .settings import (
    DOCS_TARGET_PATH,
    ORIGINS,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tags_metadata = [
    {"name": "test", "description": "Test."},
]

app = FastAPI(
    title=f"Lootbox HTTP API",
    description="Lootbox API endpoints.",
    version="v0.0.1",
    openapi_tags=tags_metadata,
    openapi_url="/openapi.json",
    docs_url=None,
    redoc_url=f"/{DOCS_TARGET_PATH}",
)

unauthenticated_paths: Dict[str, str] = {"/ping": "GET"}
app.add_middleware(BroodAuthMiddleware, whitelist=unauthenticated_paths)

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


# POST /drops - upload CSV file and register a claim for that CSV file on Dropper contract at a given address
# GET /drops/<dropper_address>/<claim_id>/<address> - get signed transaction for user with the given address [SIGNATURE WORKFLOW]
# GET /drops?dropper_address=<dropper_address>&claim_id=<claim_id>&address=<address> - list all drops with the given filters


@app.post("/drops/")
async def create_drop(register_request: data.DropRegisterRequest = Body(...)) -> None:
    print("Dropper address:", register_request.dropper_address)
    print("Claim ID:", register_request.claim_id)
    print("Addresses:", register_request.addresses)
