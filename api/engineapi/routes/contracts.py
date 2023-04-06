"""
Contract registration API

Moonstream users can register contracts on Moonstream Engine. This allows them to use these contracts
as part of their chain-adjacent activities (like performing signature-based token distributions on the
Dropper contract).
"""
import logging
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import Body, Depends, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .. import data, db
from .. import contracts_actions
from ..middleware import BroodAuthMiddleware, EngineHTTPException
from ..settings import DOCS_TARGET_PATH, ORIGINS
from ..version import VERSION

logger = logging.getLogger(__name__)


TITLE = "Moonstream Engine Contracts API"
DESCRIPTION = "Users can register contracts on the Moonstream Engine for use in chain-adjacent activities, like setting up signature-based token distributions."


tags_metadata = [
    {
        "name": "contracts",
        "description": DESCRIPTION,
    }
]


whitelist_paths = {
    "/contracts/openapi.json": "GET",
    f"/contracts/{DOCS_TARGET_PATH}": "GET",
    "/contracts/types": "GET",
    "/contracts/requests": "GET",
}

app = FastAPI(
    title=TITLE,
    description=DESCRIPTION,
    version=VERSION,
    openapi_tags=tags_metadata,
    openapi_url="/openapi.json",
    docs_url=None,
    redoc_url=f"/{DOCS_TARGET_PATH}",
)


app.add_middleware(BroodAuthMiddleware, whitelist=whitelist_paths)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/types")
async def contract_types() -> Dict[str, str]:
    """
    Describes the contract_types that users can register contracts as against this API.
    """
    return {
        contracts_actions.ContractType.raw.value: "A generic smart contract. You can ask users to submit arbitrary calldata to this contract.",
        contracts_actions.ContractType.dropper.value: "A Dropper contract. You can authorize users to submit claims against this contract.",
    }


@app.get("/")
async def list_registered_contracts(
    request: Request,
    blockchain: Optional[str] = Query(None),
    address: Optional[str] = Query(None),
    contract_type: Optional[contracts_actions.ContractType] = Query(None),
    limit: int = Query(10),
    offset: Optional[int] = Query(None),
    db_session: Session = Depends(db.yield_db_session),
) -> List[data.RegisteredContract]:
    """
    Users can use this endpoint to look up the contracts they have registered against this API.
    """
    contracts = contracts_actions.lookup_registered_contracts(
        db_session=db_session,
        moonstream_user_id=request.state.user.id,
        blockchain=blockchain,
        address=address,
        contract_type=contract_type,
        limit=limit,
        offset=offset,
    )
    return [
        contracts_actions.render_registered_contract(contract) for contract in contracts
    ]


@app.post("/register", response_model=data.RegisteredContract)
async def register_contract(
    request: Request,
    contract: data.RegisterContractRequest,
    db_session: Session = Depends(db.yield_db_session),
) -> data.RegisteredContract:
    """
    Allows users to register contracts.
    """
    try:
        registered_contract = contracts_actions.register_contract(
            db_session=db_session,
            moonstream_user_id=request.state.user.id,
            blockchain=contract.blockchain,
            address=contract.address,
            contract_type=contracts_actions.ContractType(contract.contract_type),
            title=contract.title,
            description=contract.description,
            image_uri=contract.image_uri,
        )
    except contracts_actions.ContractAlreadyRegistered:
        raise EngineHTTPException(
            status_code=409,
            detail="Contract already registered",
        )
    return contracts_actions.render_registered_contract(registered_contract)


@app.delete("/{contract_id}", response_model=data.RegisteredContract)
async def delete_contract(
    request: Request,
    contract_id: UUID,
    db_session: Session = Depends(db.yield_db_session),
) -> data.RegisteredContract:
    """
    Allows users to delete contracts that they have registered.
    """
    try:
        deleted_contract = contracts_actions.delete_registered_contract(
            db_session=db_session,
            moonstream_user_id=request.state.user.id,
            registered_contract_id=contract_id,
        )
    except Exception as err:
        logger.error(repr(err))
        raise EngineHTTPException(status_code=500)

    return contracts_actions.render_registered_contract(deleted_contract)


@app.get("/requests", response_model=List[data.CallRequest])
async def list_requests(
    contract_id: UUID = Query(...),
    caller: str = Query(...),
    limit: int = Query(100),
    offset: Optional[int] = Query(None),
    db_session: Session = Depends(db.yield_db_session),
) -> List[data.CallRequest]:
    """
    Allows API user to see all unexpired call requests for a given caller against a given contract.
    """
    try:
        requests = contracts_actions.list_call_requests(
            db_session=db_session,
            registered_contract_id=contract_id,
            caller=caller,
            limit=limit,
            offset=offset,
            show_expired=False,
        )
    except Exception as e:
        logger.error(repr(e))
        raise EngineHTTPException(status_code=500)

    return requests


@app.post("/{contract_id}/requests")
async def create_requests(
    request: Request,
    contract_id: UUID,
    data: data.CreateCallRequestsAPIRequest = Body(...),
    db_session: Session = Depends(db.yield_db_session),
) -> None:
    """
    Allows API user to register call requests from given call specifications.
    """
    try:
        call_request = contracts_actions.request_calls(
            db_session=db_session,
            moonstream_user_id=request.state.user.id,
            registered_contract_id=contract_id,
            call_specs=data.specifications,
            ttl_days=data.ttl_days,
        )
    except Exception as e:
        logger.error(repr(e))
        raise EngineHTTPException(status_code=500)

    return call_request
