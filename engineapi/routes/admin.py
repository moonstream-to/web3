"""
Moonstream Engine Admin API.
"""
import logging
from typing import List, Optional, Any
from uuid import UUID

from web3 import Web3
from brownie import network


from fastapi import APIRouter, Body, FastAPI, Request, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from engineapi.models import DropperClaimant

from .. import actions
from .. import data
from .. import db
from .. import Dropper
from .. import signatures
from ..middleware import DropperHTTPException, DropperAuthMiddleware
from ..settings import DOCS_TARGET_PATH, ORIGINS


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


@app.post("/drops", response_model=data.DropCreatedResponse)
async def create_drop(
    request: Request,
    register_request: data.DropRegisterRequest = Body(...),
    db_session: Session = Depends(db.yield_db_session),
) -> data.DropCreatedResponse:

    """
    Create a drop for a given dropper contract.
    """
    try:
        actions.ensure_dropper_contract_owner(
            db_session, register_request.dropper_contract_id, request.state.address
        )
    except actions.AuthorizationError as e:
        logger.error(e)
        raise DropperHTTPException(status_code=403)
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="Dropper contract not found")
    except Exception as e:
        logger.error(e)
        raise DropperHTTPException(status_code=500)

    if register_request.terminus_address:
        register_request.terminus_address = Web3.toChecksumAddress(
            register_request.terminus_address
        )

    try:
        claim = actions.create_claim(
            db_session=db_session,
            dropper_contract_id=register_request.dropper_contract_id,
            title=register_request.title,
            description=register_request.description,
            claim_block_deadline=register_request.claim_block_deadline,
            terminus_address=register_request.terminus_address,
            terminus_pool_id=register_request.terminus_pool_id,
            claim_id=register_request.claim_id,
        )
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="Dropper contract not found")
    except Exception as e:
        logger.error(f"Can't create claim: {e}")
        raise DropperHTTPException(status_code=500, detail="Can't create claim")

    return data.DropCreatedResponse(
        dropper_claim_id=claim.id,
        dropper_contract_id=claim.dropper_contract_id,
        title=claim.title,
        description=claim.description,
        claim_block_deadline=claim.claim_block_deadline,
        terminus_address=claim.terminus_address,
        terminus_pool_id=claim.terminus_pool_id,
        claim_id=claim.claim_id,
    )


@app.put(
    "/drops/{dropper_claim_id}/activate",
    response_model=data.DropUpdatedResponse,
)
async def activate_drop(
    request: Request,
    dropper_claim_id: UUID,
    db_session: Session = Depends(db.yield_db_session),
) -> data.DropUpdatedResponse:

    """
    Activate a given drop by drop id.
    """
    try:
        actions.ensure_admin_token_holder(
            db_session, dropper_claim_id, request.state.address
        )
    except actions.AuthorizationError as e:
        logger.error(e)
        raise DropperHTTPException(status_code=403)
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="Drop not found")

    try:
        drop = actions.activate_drop(
            db_session=db_session,
            dropper_claim_id=dropper_claim_id,
        )
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="Drop not found")
    except Exception as e:
        logger.error(f"Can't activate drop: {e}")
        raise DropperHTTPException(status_code=500, detail="Can't activate drop")

    return data.DropUpdatedResponse(
        dropper_claim_id=drop.id,
        dropper_contract_id=drop.dropper_contract_id,
        title=drop.title,
        description=drop.description,
        claim_block_deadline=drop.claim_block_deadline,
        terminus_address=drop.terminus_address,
        terminus_pool_id=drop.terminus_pool_id,
        claim_id=drop.claim_id,
        active=drop.active,
    )


@app.put(
    "/drops/{dropper_claim_id}/deactivate",
    response_model=data.DropUpdatedResponse,
)
async def deactivate_drop(
    request: Request,
    dropper_claim_id: UUID,
    db_session: Session = Depends(db.yield_db_session),
) -> data.DropUpdatedResponse:

    """
    Activate a given drop by drop id.
    """
    try:
        actions.ensure_admin_token_holder(
            db_session, dropper_claim_id, request.state.address
        )
    except actions.AuthorizationError as e:
        logger.error(e)
        raise DropperHTTPException(status_code=403)
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="Drop not found")

    try:
        drop = actions.deactivate_drop(
            db_session=db_session,
            dropper_claim_id=dropper_claim_id,
        )
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="Drop not found")
    except Exception as e:
        logger.error(f"Can't activate drop: {e}")
        raise DropperHTTPException(status_code=500, detail="Can't activate drop")

    return data.DropUpdatedResponse(
        dropper_claim_id=drop.id,
        dropper_contract_id=drop.dropper_contract_id,
        title=drop.title,
        description=drop.description,
        claim_block_deadline=drop.claim_block_deadline,
        terminus_address=drop.terminus_address,
        terminus_pool_id=drop.terminus_pool_id,
        claim_id=drop.claim_id,
        active=drop.active,
    )


@app.patch("/drops/{dropper_claim_id}", response_model=data.DropUpdatedResponse)
async def update_drop(
    request: Request,
    dropper_claim_id: UUID,
    update_request: data.DropUpdateRequest = Body(...),
    db_session: Session = Depends(db.yield_db_session),
) -> data.DropUpdatedResponse:

    """
    Update a given drop by drop id.
    """
    try:
        actions.ensure_admin_token_holder(
            db_session, dropper_claim_id, request.state.address
        )
    except actions.AuthorizationError as e:
        logger.error(e)
        raise DropperHTTPException(status_code=403)
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="Drop not found")

    try:
        drop = actions.update_drop(
            db_session=db_session,
            dropper_claim_id=dropper_claim_id,
            title=update_request.title,
            description=update_request.description,
            claim_block_deadline=update_request.claim_block_deadline,
            terminus_address=update_request.terminus_address,
            terminus_pool_id=update_request.terminus_pool_id,
            claim_id=update_request.claim_id,
            address=request.state.address,
        )
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="Drop not found")
    except Exception as e:
        logger.error(f"Can't update drop: {e}")
        raise DropperHTTPException(status_code=500, detail="Can't update drop")

    return data.DropUpdatedResponse(
        dropper_claim_id=drop.id,
        dropper_contract_id=drop.dropper_contract_id,
        title=drop.title,
        description=drop.description,
        claim_block_deadline=drop.claim_block_deadline,
        terminus_address=drop.terminus_address,
        terminus_pool_id=drop.terminus_pool_id,
        claim_id=drop.claim_id,
        active=drop.active,
    )


@app.get("/drops/{dropper_claim_id}/claimants", response_model=data.DropListResponse)
async def get_claimants(
    request: Request,
    dropper_claim_id: UUID,
    limit: int = 10,
    offset: int = 0,
    db_session: Session = Depends(db.yield_db_session),
) -> data.DropListResponse:
    """
    Get list of claimants for a given dropper contract.
    """

    try:
        actions.ensure_admin_token_holder(
            db_session, dropper_claim_id, request.state.address
        )
    except actions.AuthorizationError as e:
        logger.error(e)
        raise DropperHTTPException(status_code=403)
    except Exception as e:
        logger.error(e)
        raise DropperHTTPException(status_code=500)

    try:
        results = actions.get_claimants(
            db_session=db_session,
            dropper_claim_id=dropper_claim_id,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        logger.info(f"Can't add claimants for claim {dropper_claim_id} with error: {e}")
        raise DropperHTTPException(status_code=500, detail=f"Error adding claimants")

    return data.DropListResponse(drops=list(results))


@app.post(
    "/drops/{dropper_claim_id}/claimants/batch", response_model=data.ClaimantsResponse
)
async def add_claimants(
    request: Request,
    dropper_claim_id: UUID,
    claimants_list: List[data.Claimant] = Body(...),
    db_session: Session = Depends(db.yield_db_session),
) -> data.ClaimantsResponse:
    """
    Add addresses to particular claim
    """

    try:
        actions.ensure_admin_token_holder(
            db_session, dropper_claim_id, request.state.address
        )
    except actions.AuthorizationError as e:
        logger.error(e)
        raise DropperHTTPException(status_code=403)
    except Exception as e:
        logger.error(e)
        raise DropperHTTPException(status_code=500)

    try:
        results = actions.add_claimants(
            db_session=db_session,
            dropper_claim_id=dropper_claim_id,
            claimants=claimants_list,
            added_by=request.state.address,
        )
    except Exception as e:
        logger.info(f"Can't add claimants for claim {dropper_claim_id} with error: {e}")
        raise DropperHTTPException(status_code=500, detail=f"Error adding claimants")

    return data.ClaimantsResponse(claimants=results)


@app.delete("/claimants", response_model=data.RemoveClaimantsResponse)
async def delete_claimants(
    request: Request,
    remove_claimants_request: data.DropRemoveClaimantsRequest = Body(...),
    db_session: Session = Depends(db.yield_db_session),
) -> data.RemoveClaimantsResponse:

    """
    Remove addresses to particular claim
    """

    try:
        actions.ensure_admin_token_holder(
            db_session,
            remove_claimants_request.dropper_claim_id,
            request.state.address,
        )
    except actions.AuthorizationError as e:
        logger.error(e)
        raise DropperHTTPException(status_code=403)
    except Exception as e:
        logger.error(e)
        raise DropperHTTPException(status_code=500)

    try:
        results = actions.delete_claimants(
            db_session=db_session,
            dropper_claim_id=remove_claimants_request.dropper_claim_id,
            addresses=remove_claimants_request.addresses,
        )
    except Exception as e:
        logger.info(
            f"Can't remove claimants for claim {remove_claimants_request.dropper_claim_id} with error: {e}"
        )
        raise DropperHTTPException(status_code=500, detail=f"Error removing claimants")

    return data.RemoveClaimantsResponse(addresses=results)


@app.get("/claimants/search", response_model=data.Claimant)
async def get_claimant_in_drop(
    request: Request,
    dropper_claim_id: UUID,
    address: str,
    db_session: Session = Depends(db.yield_db_session),
) -> data.Claimant:

    """
    Return claimant from drop
    """
    try:
        actions.ensure_admin_token_holder(
            db_session,
            dropper_claim_id,
            request.state.address,
        )
    except actions.AuthorizationError as e:
        logger.error(e)
        raise DropperHTTPException(status_code=403)
    except Exception as e:
        logger.error(e)
        raise DropperHTTPException(status_code=500)

    try:
        claimant = actions.get_claimant(
            db_session=db_session,
            dropper_claim_id=dropper_claim_id,
            address=address,
        )

    except NoResultFound:
        raise DropperHTTPException(
            status_code=404, detail="Address not present in that drop."
        )
    except Exception as e:
        logger.error(f"Can't get claimant: {e}")
        raise DropperHTTPException(status_code=500, detail="Can't get claimant")

    return data.Claimant(address=claimant.address, amount=claimant.amount)


@app.post("/drop/{dropper_claim_id}/refetch")
async def refetch_drop_signatures(
    request: Request,
    dropper_claim_id: UUID,
    db_session: Session = Depends(db.yield_db_session),
) -> Any:
    """
    Refetch signatures for a drop
    """

    try:
        actions.ensure_admin_token_holder(
            db_session, dropper_claim_id, request.state.address
        )
    except actions.AuthorizationError as e:
        logger.error(e)
        raise DropperHTTPException(status_code=403)
    except Exception as e:
        logger.error(e)
        raise DropperHTTPException(status_code=500)

    try:
        signatures = actions.refetch_drop_signatures(
            db_session=db_session, dropper_claim_id=dropper_claim_id
        )
    except Exception as e:
        logger.info(
            f"Can't refetch signatures for drop {dropper_claim_id} with error: {e}"
        )
        raise DropperHTTPException(
            status_code=500, detail=f"Error refetching signatures"
        )

    return signatures
