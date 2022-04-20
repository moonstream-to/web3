"""
Lootbox API.
"""
import logging
from typing import List

from brownie import network, web3
from bugout.data import BugoutJournalEntry
from bugout.exceptions import BugoutResponseException

from fastapi import Body, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from . import actions
from . import data
from . import Dropper
from . import signatures
from .middleware import BearerTokenMiddleware, DropperHTTPException
from .settings import (
    BROWNIE_NETWORK,
    DOCS_TARGET_PATH,
    ORIGINS,
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

# app.add_middleware(BearerTokenMiddleware)

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


@app.get("/drops", response_model=data.DropResponse)
async def get_drop_handler(dropper_claim_id: int, address: str) -> data.DropResponse:
    """
    Get signed transaction for user with the given address.
    example:
    curl -X GET "http://localhost:8000/drops?claim_id=<claim_number>&address=<user_address>"
    """

    address = web3.toChecksumAddress(address)

    try:
        results = actions.get_claimants(dropper_claim_id, address)
    except Exception as e:
        raise DropperHTTPException(status_code=e.status_code, detail=e.detail)

    if len(results) == 0:
        raise DropperHTTPException(
            status_code=404, detail="Whitelist or address not found"
        )
    elif len(results) > 1:
        # TODO: In the future, this case should not be a failure.
        logger.error(
            f"Multiple whitelists found for claim_id {dropper_claim_id} and address {address}"
        )
        raise DropperHTTPException(status_code=409, detail="Too many whitelists found")

    address, amount, claim_id = results[0]

    drop_deadline = len(network.chain) + 100

    message_hash = DROPPER.claim_message_hash(claim_id, address, drop_deadline, amount)

    try:
        signature = signatures.DROP_SIGNER.sign_message(message_hash)
    except signatures.AWSDescribeInstancesFail:
        raise DropperHTTPException(status_code=500)
    except signatures.SignWithInstanceFail:
        raise DropperHTTPException(status_code=500)
    except Exception as err:
        raise DropperHTTPException(status_code=500)
    return data.DropResponse(
        claimant=address,
        claim_id=claim_id,
        block_deadline=drop_deadline,
        signature=signature,
    )


@app.get("/drops/claims", response_model=data.DropListResponse)
async def get_drop_list_handler(
    request: Request, dropper_contract_address: str, blockchain: str, address: str
) -> data.DropListResponse:
    """
    Get list of drops for a given dropper contract and claimant address.
    1 address can have multiple contracts?
    """

    address = web3.toChecksumAddress(address)

    try:
        results = actions.get_claims(dropper_contract_address, blockchain, address)
    except BugoutResponseException as e:
        raise DropperHTTPException(status_code=e.status_code, detail=e.detail)

    return data.DropListResponse(drops=results)


@app.post("/drops/claims", response_model=BugoutJournalEntry)
async def create_drop(
    request: Request, register_request: data.DropRegisterRequest = Body(...)
) -> List[str]:

    """
    Create a drop for a given dropper contract.
    required: Web3 verification of signature (middleware probably)
    body:
        dropper_contract_address: address of dropper contract
        claim_id: claim id
        address: address of claimant
        amount: amount of drop

    """
    logger.info(f"Creating drop for {DROPPER_ADDRESS}")

    try:
        claim = actions.create_claim(
            dropper_contract_address=register_request.dropper_contract_address,
            blockchain=register_request.blockchain,
            title=register_request.title,
            description=register_request.description,
            claim_block_deadline=register_request.claim_block_deadline,
            terminus_address=register_request.terminus_address,
            terminus_pool_id=register_request.terminus_pool_id,
            claim_id=register_request.claim_id,
        )
    except Exception as e:
        raise DropperHTTPException(status_code=e.status_code, detail=e.detail)

    return claim


@app.get("/drops/claimants", response_model=data.DropResponse)
async def get_claimants(
    dropper_claim_id: str, limit: int = 10, offset: int = 0
) -> List[str]:
    """
    Get list of claimants for a given dropper contract.
    """
    try:
        results = actions.get_claimants(dropper_claim_id, limit, offset)
    except Exception as e:
        raise DropperHTTPException(status_code=e.status_code, detail=e.detail)

    return results


@app.post("/drops/claimants", response_model=data.DropResponse)
async def create_claimants(
    request: Request, add_claimants_request: data.DropAddClaimantsRequest = Body(...)
) -> List[str]:

    """
    Add addresses to particular claim
    """

    added_by = "me"  # request.state.user.address read from header in auth middleware

    try:
        results = actions.add_claimants(
            dropper_claim_id=add_claimants_request.dropper_claim_id,
            claimants=add_claimants_request.claimants,
            added_by=added_by,
        )
    except Exception as e:
        raise DropperHTTPException(status_code=500, detail=e.detail)

    return results


@app.delete("/drops/claimants", response_model=data.DropResponse)
async def create_claimants(
    request: Request,
    remove_claimants_request: data.DropRemoveClaimantsRequest = Body(...),
) -> List[str]:

    """
    Remove addresses to particular claim
    """

    try:
        results = actions.delete_claimants(
            dropper_claim_id=remove_claimants_request.dropper_claim_id,
            addresses=remove_claimants_request.addresses,
        )
    except Exception as e:
        raise DropperHTTPException(status_code=500, detail=e.detail)

    return results
