"""
Lootbox API.
"""
import logging
from typing import Dict, List
import uuid

from fastapi import Body, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from . import data
from .middleware import BroodAuthMiddleware
from .settings import (
    MOONSTREAM_ENGINE_APPLICATION_ID,
    bugout_client as bc,
    DOCS_TARGET_PATH,
    ORIGINS,
)

RESOURCE_TYPE_DROP_WHITELIST = "drop_whitelist"

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


# POST /drops - add an address for a drop
# DELETE /drops - remove an address from a drop
# GET /drops/<dropper_address>/<claim_id>/<address> - get signed transaction for user with the given address [SIGNATURE WORKFLOW]
# GET /drops?dropper_address=<dropper_address>&claim_id=<claim_id>&address=<address> - list all drops with the given filters

# TODO: Do this with journals instead of resources!!!


@app.post("/drops/")
async def create_drop(
    request: Request, register_request: data.DropRegisterRequest = Body(...)
) -> List[str]:
    user = request.state.user
    # TODO(zomglings): Check if user has permission to add to whitelist for drop.
    bugout_access_token = request.state.token
    resource_ids: List[str] = []
    for address in register_request.addresses:
        resource = bc.resource.create_resource(
            bugout_access_token,
            MOONSTREAM_ENGINE_APPLICATION_ID,
            {
                "type": RESOURCE_TYPE_DROP_WHITELIST,
                "dropper_address": register_request.dropper_address,
                "claim_id": register_request.claim_id,
                "address": address,
            },
        )
        resource_ids.append(str(resource.id))

    return resource_ids
