"""
Contract registration API

Moonstream users can register contracts on Moonstream Engine. This allows them to use these contracts
as part of their chain-adjacent activities (like performing signature-based token distributions on the
Dropper contract).
"""
import logging
from uuid import UUID

from fastapi import FastAPI, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from typing import Any, Dict, List, Optional

from .. import registered_contracts as registered_contracts_actions
from .. import data
from .. import db
from ..middleware import BroodAuthMiddleware, EngineHTTPException
from ..settings import DOCS_TARGET_PATH, ORIGINS
from ..version import VERSION

logger = logging.getLogger(__name__)


TITLE = "Moonstream Engine registered contracts"
DESCRIPTION = "Users can register contracts on the Moonstream Engine for user in chain-adjacent activities, like setting up signature-based token distributions."


tags_metadata = [
    {
        "name": "contracts",
        "description": DESCRIPTION,
    }
]


whitelist_paths = {}

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


@app.get("/")
async def list_registered_contracts(
    request: Request,
    blockchain: Optional[str] = Query(None),
    address: Optional[str] = Query(None),
    contract_type: Optional[str] = Query(None),
    limit: int = Query(10),
    offset: Optional[int] = Query(None),
    db_session: Session = Depends(db.yield_db_session),
) -> List[data.RegisteredContract]:
    contracts = registered_contracts_actions.lookup_registered_contracts(
        db_session=db_session,
        moonstream_user_id=request.state.user.id,
        blockchain=blockchain,
        address=address,
        contract_type=contract_type,
        limit=limit,
        offset=offset,
    )
    return [
        registered_contracts_actions.render_registered_contract(contract)
        for contract in contracts
    ]
