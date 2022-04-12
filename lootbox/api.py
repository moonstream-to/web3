"""
Lootbox API.
"""
from inspect import signature
from lib2to3.pgen2 import token
import logging
from typing import Dict, List
from urllib import response
import uuid
from certifi import contents


from bugout.data import BugoutJournals
from bugout.exceptions import BugoutResponseException

from fastapi import Body, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from matplotlib.pyplot import title

from . import data
from .middleware import BroodAuthMiddleware, DropperHTTPException
from .settings import (
    MOONSTREAM_ENGINE_APPLICATION_ID,
    MOONSTREAM_ENGINE_ADMIN_ACCESS_TOKEN,
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




def get_drop_journal_id(token: str, journal_name: str) -> str:
    """
    Get a new drop journal id.
    """
    try:
        response: BugoutJournals = bc.list_journals(token=token)
    except BugoutResponseException as e:
        raise DropperHTTPException(status_code=e.status_code, detail=e.detail)
    
    for journal in response.journals:
        if journal.name == journal_name:
            return journal.id
    
    try:
        response = bc.create_journal(journal_name)
    except BugoutResponseException as e:
        raise DropperHTTPException(status_code=e.status_code, detail=e.detail)
    

    return response.get("id")


def internal_request_to_signer_server(drop_name: str, dropper_address: str, claim_id: str, addresses: List[str]) -> str:
    """
    Rrquest to signer server.
    """

    return "signed_transaction"


@app.get("/drops/<dropper_address>/<claim_id>/<address>", response_model=data.DropResponse)
async def get_drop_handler(
    dropper_address: str, claim_id: str, address: str
) -> data.DropResponse:
    """
    Get signed transaction for user with the given address.
    """
    signature = internal_request_to_signer_server(dropper_address, claim_id, address)
    return data.DropResponse(signed_transaction=signature)

@app.get("/drops", response_model=data.DropListResponse)
async def get_drop_list_handler(
    request: Request,
    dropper_address: str = Query(None),
    claim_id: str = Query(None),
    address: str = Query(None),
) -> data.DropListResponse:
    """
    Get list of drops with the given filters.
    """
    token = request.state.get("token")

    tags = []

    if dropper_address is not None:
        tags.append(f"dropper_address={dropper_address}")
    
    if claim_id is not None:
        tags.append(f"claim_id={claim_id}")
    
    if address is not None:
        query=f"{address} tag:claim_id:{claim_id} tag:dropper_address:{dropper_address}"
    else:
        query=f"tag:claim_id:{claim_id} tag:dropper_address:{dropper_address}"

    try:
        response = bc.search(
            token=token,
            journal_id=get_drop_journal_id(token, "drop_whitelist"),
            query=query,
            limit=100,
            offset=0,
            sort_by="created_at",
            sort_order="desc",
        )
    except BugoutResponseException as e:
        raise DropperHTTPException(status_code=e.status_code, detail=e.detail)
    return data.DropListResponse(drops=response.results)


@app.post("/drops", response_model=data.DropRegisterResponse)
async def create_drop(
    request: Request, register_request: data.DropRegisterRequest = Body(...)
) -> List[str]:

    """
    Drops give ability upload whitelisted addresses to a specific claim.
    """
    logger.info(f"Creating drop for {register_request.dropper_address}")

    # Us bugout entry as storage for the whitelist

    token = request.state.token


    # Get the drop journal id
    journal_id = get_drop_journal_id(token, "drop_whitelist") # add it to register_request body or not? What you think github copilot?  -_- 
    # search that user's bugout entry if it exists
    try:
        response = bc.search(
                token=token,
                journal_id=journal_id,
                query=f"tag:claim_id:{register_request.claim_id} tag:dropper_address:{register_request.dropper_address}",
                limit=1,
                content=False,
                timeout=10.0
            )
    except BugoutResponseException as e:
        raise DropperHTTPException(status_code=e.status_code, detail=e.detail)

    if len(response.results) == 0:
        # create a new bugout entry
        try:
            drop_entry = bc.create_journal_entry(
                token=token,
                journal_id=journal_id,
                title=f"{register_request.name}",
                tags=[f"claim_id:{register_request.claim_id}", f"dropper_address:{register_request.dropper_address}"],
                content=f"{'\n'.join(list(set(register_request.addresses)))}",
                timeout=10.0,
                context_type="csv",
            )
        except BugoutResponseException as e:
            raise DropperHTTPException(status_code=e.status_code, detail=e.detail)
    else:
        # update the existing bugout entry
        new_addresses = response.results[0].get("content").split("\n").extend(register_request.addresses)
        try:
            drop_entry = bc.update_journal_entry(
                token=token,
                journal_id=journal_id,
                entry_id=response.results[0].get("id"),
                title=f"{register_request.name}",
                tags=[f"claim_id:{register_request.claim_id}", f"dropper_address:{register_request.dropper_address}"],
                content=f"{'\n'.join(list(set(new_addresses)))}",
                timeout=10.0,
            )
        except BugoutResponseException as e:
            raise DropperHTTPException(status_code=e.status_code, detail=e.detail)

    return drop_entry


@app.delete("/drops", response_model=data.DropRegisterResponse)
async def delete_drop(
    request: Request, delete_request: data.DropRegisterRequest = Body(...)
) -> List[str]:

    """
    Drops give ability upload whitelisted addresses to a specific claim.
    """
    logger.info(f"Deleting drop for {delete_request.dropper_address}")

    # Us bugout entry as storage for the whitelist

    token = request.state.token


    # Get the drop journal id
    journal_id = get_drop_journal_id(token, "drop_whitelist")

    # search that user's bugout entry if it exists
    try:
        response = bc.search(
                token=token,
                journal_id=journal_id,
                query=f"tag:claim_id:{delete_request.claim_id} tag:dropper_address:{delete_request.dropper_address}",
                limit=1,
                content=False,
                timeout=10.0
            )
    except Exception as e:
        logger.error(f"Bugout error: {e}")
        raise e

    if len(response.results) == 0:
        return []

    else:
        # delete addresses from existing bugout entry
        try:
            drop_entry = bc.update_journal_entry(
                token=token,
                journal_id=journal_id,
                entry_id=response.results[0].get("id"),
                content=f"{'\n'.join(list(set([address for address in response.results[0].get('content').split('\n') not in delete_request.addresses])))}",
                timeout=10.0,

            )
        except Exception as e:
            logger.error(f"Bugout error: {e}")
            raise e

    return drop_entry

