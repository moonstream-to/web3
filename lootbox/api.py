"""
Lootbox API.
"""
import logging
from typing import List

from brownie import network
from bugout.data import BugoutJournalEntry
from bugout.exceptions import BugoutResponseException

from fastapi import Body, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from . import data
from . import Dropper
from .middleware import BearerTokenMiddleware, DropperHTTPException
from .settings import (
    BROWNIE_NETWORK,
    MOONSTREAM_ENGINE_ADMIN_ACCESS_TOKEN,
    bugout_client as bc,
    DOCS_TARGET_PATH,
    ORIGINS,
    DROP_JOURNAL_ID,
    DROP_SIGNER,
    DROPPER_ADDRESS,
)

network.connect(BROWNIE_NETWORK)

DROPPER = Dropper.Dropper(DROPPER_ADDRESS)

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

app.add_middleware(BearerTokenMiddleware)

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


@app.get("/drops", response_model=data.DropResponse)
async def get_drop_handler(claim_id: int, address: str) -> data.DropResponse:
    """
    Get signed transaction for user with the given address.
    example:
    curl -X GET "http://localhost:8000/drops?claim_id=<claim_number>&address=<user_address>"
    """
    try:
        response = bc.search(
            token=MOONSTREAM_ENGINE_ADMIN_ACCESS_TOKEN,
            journal_id=DROP_JOURNAL_ID,
            query=f"tag:claim_id:{claim_id} tag:dropper_address:{DROPPER_ADDRESS}",
            content=True,
            timeout=10.0,
        )
    except BugoutResponseException as e:
        raise DropperHTTPException(status_code=e.status_code, detail=e.detail)

    if len(response.results) == 0:
        raise DropperHTTPException(status_code=404, detail="Whitelist not found")
    elif len(response.results) > 1:
        # TODO: In the future, this case should not be a failure.
        raise DropperHTTPException(status_code=409, detail="Too many whitelists found")
    else:
        addresses = set(response.results[0].content.strip().split("\n"))

    if address not in addresses:
        raise DropperHTTPException(
            status_code=403, detail=f"Address not in whitelist: {address}"
        )

    drop_deadline = len(network.chain) + 100

    message_hash = DROPPER.claim_message_hash(
        claim_id,
        address,
        drop_deadline,
    )

    signature = DROP_SIGNER.sign_message(message_hash)
    return data.DropResponse(
        claimant=address,
        claim_id=claim_id,
        block_deadline=drop_deadline,
        signature=signature,
    )


@app.get("/drops/search", response_model=data.DropListResponse)
async def get_drop_list_handler(
    request: Request,
    drop_name: str = Query(None),
    claim_id: str = Query(None),
    address: str = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
) -> data.DropListResponse:
    """
    Get list of drops with the given filters.
    example:
    curl -X GET -H "Authorization: Bearer <token>"  http://localhost:8000/drops/search?dropper_address=0x1&drop_name=test&claim_id=1
    """
    token = request.state.token

    query_list = [f"tad:dropper_address:{DROPPER}"]

    if claim_id is not None:
        query_list.append(f"tag:claim_id:{claim_id}")

    if drop_name is not None:
        query_list.append(drop_name)

    query = " ".join(query_list)
    try:
        response = bc.search(
            token=token,
            journal_id=DROP_JOURNAL_ID,
            query=query,
            limit=limit,
            offset=offset,
        )
    except BugoutResponseException as e:
        raise DropperHTTPException(status_code=e.status_code, detail=e.detail)

    if len(response.results) > 0 and address is not None:
        # Filter by address
        for entry_index, result in enumerate(response.results):
            addresses = set(result.content.strip().split("\n"))
            if address not in addresses:
                response.results.remove(result)
            else:
                response.results[entry_index]["content"]
        return data.DropListResponse(drops=response.results)

    return data.DropListResponse(drops=response.results)


@app.post("/drops", response_model=BugoutJournalEntry)
async def create_drop(
    request: Request, register_request: data.DropRegisterRequest = Body(...)
) -> List[str]:

    """
    Drops give ability upload whitelisted addresses to a specific claim.
    example:
    curl -X POST -H "Content-Type: application/json" -H "authorization: bearer <token>" -d '{"name":"test", "dropper_address": "", "claim_id": "1", "addresses": ["0x1", "0x2"]}' http://localhost:8000/drops
    """
    logger.info(f"Creating drop for {DROPPER_ADDRESS}")

    # Us bugout entry as storage for the whitelist

    token = request.state.token

    # search that user's bugout entry if it exists
    try:
        response = bc.search(
            token=token,
            journal_id=DROP_JOURNAL_ID,
            query=f"tag:claim_id:{register_request.claim_id} tag:dropper_address:{DROPPER_ADDRESS}",
            limit=1,
            content=False,
            timeout=10.0,
        )
    except BugoutResponseException as e:
        raise DropperHTTPException(status_code=e.status_code, detail=e.detail)

    if len(response.results) == 0:
        content = "\n".join(list(set(register_request.addresses)))
        # create a new bugout entry
        try:
            drop_entry = bc.create_entry(
                token=token,
                journal_id=DROP_JOURNAL_ID,
                title=register_request.name,
                tags=[
                    f"claim_id:{register_request.claim_id}",
                    f"dropper_address:{DROPPER_ADDRESS}",
                ],
                content=content,
                timeout=10.0,
                context_type="csv",
            )
        except BugoutResponseException as e:
            raise DropperHTTPException(status_code=e.status_code, detail=e.detail)
    else:
        content = "\n".join(list(set(new_addresses)))
        # update the existing bugout entry
        new_addresses = (
            response.results[0]
            .get("content")
            .split("\n")
            .extend(register_request.addresses)
        )
        try:
            drop_entry = bc.update_entry_content(
                token=token,
                journal_id=DROP_JOURNAL_ID,
                entry_id=response.results[0].get("id"),
                title=register_request.name,
                tags=[
                    f"claim_id:{register_request.claim_id}",
                    f"dropper_address:{DROPPER_ADDRESS}",
                ],
                content=content,
                timeout=10.0,
            )
        except BugoutResponseException as e:
            raise DropperHTTPException(status_code=e.status_code, detail=e.detail)

    return drop_entry


@app.delete("/drops", response_model=BugoutJournalEntry)
async def delete_drop(
    request: Request, delete_request: data.DropRegisterRequest = Body(...)
) -> List[str]:

    """
    Drops give ability upload whitelisted addresses to a specific claim.
    """
    logger.info(f"Deleting drop for {delete_request.dropper_address}")

    # Us bugout entry as storage for the whitelist

    token = request.state.token

    # search that user's bugout entry if it exists
    try:
        response = bc.search(
            token=token,
            journal_id=DROP_JOURNAL_ID,
            query=f"tag:claim_id:{delete_request.claim_id} tag:dropper_address:{delete_request.dropper_address}",
            limit=1,
            content=False,
            timeout=10.0,
        )
    except Exception as e:
        logger.error(f"Bugout error: {e}")
        raise e

    if len(response.results) == 0:
        return []
    else:
        content = "\n".join(
            list(
                set(
                    [
                        address
                        for address in response.results[0].get("content").split("\n")
                        not in delete_request.addresses
                    ]
                )
            )
        )
        # delete addresses from existing bugout entry
        try:
            drop_entry = bc.update_entry_content(
                token=token,
                journal_id=DROP_JOURNAL_ID,
                entry_id=response.results[0].get("id"),
                content=content,
                timeout=10.0,
            )
        except Exception as e:
            logger.error(f"Bugout error: {e}")
            raise e

    return drop_entry
