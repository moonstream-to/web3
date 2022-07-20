"""
Moonstream Engine Play API.
"""
import logging
from pydoc import render_doc
from typing import List, Optional
from uuid import UUID


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3
from brownie import network


from fastapi import Request, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from engineapi.models import DropperClaimant


from .. import actions
from .. import data
from ..middleware import DropperHTTPException
from .. import db
from .. import Dropper
from .. import signatures
from ..middleware import DropperHTTPException
from ..settings import ENGINE_BROWNIE_NETWORK, DOCS_TARGET_PATH, DOCS_TARGET_PATH_OPENAPI

try:
    network.connect(ENGINE_BROWNIE_NETWORK)
except:
    pass


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tags_metadata = [{"name": "Play", "description": "Moonstream Engine Play API"}]


app = FastAPI(
    title=f"Moonstream Engine Play API",
    description="Moonstream Engine Play API endpoints.",
    version="v0.0.1",
    openapi_tags=tags_metadata,
    openapi_url="/openapi.json",
    docs_url=None,
    #redoc_url=f"/{DOCS_TARGET_PATH_OPENAPI['play']}",
    redoc_url=f"/{DOCS_TARGET_PATH}",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping", response_model=data.PingResponse)
async def ping_handler() -> data.PingResponse:
    """
    Check server status.
    """
    return data.PingResponse(status="ok")


@app.get("/blockchains")
async def get_drops_blockchains_handler(
    db_session: Session = Depends(db.yield_db_session),
) -> List[data.DropperBlockchainResponse]:
    """
    Get list of blockchains.
    """

    try:
        results = actions.list_drops_blockchains(db_session=db_session)
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="No drops found.")
    except Exception as e:
        logger.error(f"Can't get list of drops end with error: {e}")
        raise DropperHTTPException(status_code=500, detail="Can't get drops")

    response = [
        data.DropperBlockchainResponse(
            blockchain=result.blockchain,
        )
        for result in results
    ]

    return response


@app.get("/claims/batch", response_model=List[data.DropBatchResponseItem])
async def get_drop_batch_handler(
    blockchain: str,
    address: str,
    limit: int = 10,
    offset: int = 0,
    db_session: Session = Depends(db.yield_db_session),
) -> List[data.DropBatchResponseItem]:
    """
    Get signed transaction for all user drops.
    """

    address = Web3.toChecksumAddress(address)

    try:
        claimant_drops = actions.get_claimant_drops(
            db_session, blockchain, address, limit, offset
        )
    except NoResultFound:
        raise DropperHTTPException(
            status_code=403, detail="You are not authorized to claim that reward"
        )
    except Exception as e:
        logger.error(e)
        raise DropperHTTPException(status_code=500, detail="Can't get claimant")

    # get claimants
    try:
        claimants = (
            db_session.query(DropperClaimant)
            .filter(
                DropperClaimant.id.in_(
                    [item.dropper_claimant_id for item in claimant_drops]
                )
            )
            .all()
        )
    except Exception as err:
        logger.error(f"Can't get claimant objects for address: {address}")
        raise DropperHTTPException(
            status_code=500, detail="Can't get claimant objects."
        )

    claimants_dict = {item.id: item for item in claimants}

    # generate list of claims

    claims: List[data.DropBatchResponseItem] = []

    commit_required = False

    for claimant_drop in claimant_drops:

        transformed_amount = actions.transform_claim_amount(
            db_session, claimant_drop.dropper_claim_id, claimant_drop.amount
        )
        signature = claimant_drop.signature
        if signature is None or not claimant_drop.is_recent_signature:
            dropper_contract = Dropper.Dropper(claimant_drop.dropper_contract_address)

            message_hash = dropper_contract.claim_message_hash(
                claimant_drop.claim_id,
                claimant_drop.address,
                claimant_drop.claim_block_deadline,
                transformed_amount,
            )

            try:
                signature = signatures.DROP_SIGNER.sign_message(message_hash)
                claimants_dict[claimant_drop.dropper_claimant_id].signature = signature
                commit_required = True
            except signatures.AWSDescribeInstancesFail:
                raise DropperHTTPException(status_code=500)
            except signatures.SignWithInstanceFail:
                raise DropperHTTPException(status_code=500)
            except Exception as err:
                logger.error(f"Unexpected error in signing message process: {err}")
                raise DropperHTTPException(status_code=500)

        claims.append(
            data.DropBatchResponseItem(
                claimant=claimant_drop.address,
                amount=transformed_amount,
                amount_string=str(transformed_amount),
                claim_id=claimant_drop.claim_id,
                block_deadline=claimant_drop.claim_block_deadline,
                signature=signature,
                dropper_claim_id=claimant_drop.dropper_claim_id,
                dropper_contract_address=claimant_drop.dropper_contract_address,
                blockchain=claimant_drop.blockchain,
                active=claimant_drop.active,
                title=claimant_drop.title,
                description=claimant_drop.description,
            )
        )

    if commit_required:
        db_session.commit()

    return claims


@app.get("/claims/{dropper_claim_id}", response_model=data.DropResponse)
async def get_drop_handler(
    dropper_claim_id: UUID,
    address: str,
    db_session: Session = Depends(db.yield_db_session),
) -> data.DropResponse:
    """
    Get signed transaction for user with the given address for that claim.
    """

    address = Web3.toChecksumAddress(address)

    try:
        claimant = actions.get_claimant(db_session, dropper_claim_id, address)
    except NoResultFound:
        raise DropperHTTPException(
            status_code=403, detail="You are not authorized to claim that reward"
        )
    except Exception as e:
        raise DropperHTTPException(status_code=500, detail="Can't get claimant")

    try:
        claimant_db_object = (
            db_session.query(DropperClaimant)
            .filter(DropperClaimant.id == claimant.dropper_claimant_id)
            .one()
        )
    except Exception as err:
        logger.error(
            f"Can't get claimant object for drop: {dropper_claim_id} and address: {address}"
        )
        raise DropperHTTPException(status_code=500, detail="Can't get claimant object.")

    transformed_amount = actions.transform_claim_amount(
        db_session, dropper_claim_id, claimant.amount
    )

    if not claimant.active:
        raise DropperHTTPException(
            status_code=403, detail="Cannot claim rewards for an inactive claim"
        )

    # If block deadline has already been exceeded - the contract (or frontend) will handle it.
    if claimant.claim_block_deadline is None:
        raise DropperHTTPException(
            status_code=403,
            detail="Cannot claim rewards for a claim with no block deadline",
        )
    signature = claimant.signature
    if signature is None or not claimant.is_recent_signature:
        dropper_contract = Dropper.Dropper(claimant.dropper_contract_address)
        message_hash = dropper_contract.claim_message_hash(
            claimant.claim_id,
            claimant.address,
            claimant.claim_block_deadline,
            transformed_amount,
        )

        try:
            signature = signatures.DROP_SIGNER.sign_message(message_hash)
            claimant_db_object.signature = signature
            db_session.commit()
        except signatures.AWSDescribeInstancesFail:
            raise DropperHTTPException(status_code=500)
        except signatures.SignWithInstanceFail:
            raise DropperHTTPException(status_code=500)
        except Exception as err:
            logger.error(f"Unexpected error in signing message process: {err}")
            raise DropperHTTPException(status_code=500)

    return data.DropResponse(
        claimant=claimant.address,
        amount=transformed_amount,
        claim_id=claimant.claim_id,
        block_deadline=claimant.claim_block_deadline,
        signature=signature,
        title=claimant.title,
        description=claimant.description,
    )


@app.get("/drops", response_model=data.DropListResponse)
async def get_drop_list_handler(
    blockchain: str,
    claimant_address: str,
    dropper_contract_address: Optional[str] = Query(None),
    terminus_address: Optional[str] = Query(None),
    terminus_pool_id: Optional[int] = Query(None),
    active: Optional[bool] = Query(None),
    limit: int = 20,
    offset: int = 0,
    db_session: Session = Depends(db.yield_db_session),
) -> data.DropListResponse:
    """
    Get list of drops for a given dropper contract and claimant address.
    """

    if dropper_contract_address:
        dropper_contract_address = Web3.toChecksumAddress(dropper_contract_address)

    if claimant_address:
        claimant_address = Web3.toChecksumAddress(claimant_address)

    if terminus_address:
        terminus_address = Web3.toChecksumAddress(terminus_address)

    try:
        results = actions.get_claims(
            db_session=db_session,
            dropper_contract_address=dropper_contract_address,
            blockchain=blockchain,
            claimant_address=claimant_address,
            terminus_address=terminus_address,
            terminus_pool_id=terminus_pool_id,
            active=active,
            limit=limit,
            offset=offset,
        )
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="No drops found.")
    except Exception as e:
        logger.error(
            f"Can't get claims for user {claimant_address} end with error: {e}"
        )
        raise DropperHTTPException(status_code=500, detail="Can't get claims")

    return data.DropListResponse(drops=[result for result in results])


@app.get("/drops/contracts", response_model=List[data.DropperContractResponse])
async def get_dropper_contracts_handler(
    blockchain: Optional[str] = Query(None),
    db_session: Session = Depends(db.yield_db_session),
) -> List[data.DropperContractResponse]:
    """
    Get list of drops for a given dropper contract.
    """

    try:
        results = actions.list_dropper_contracts(
            db_session=db_session, blockchain=blockchain
        )
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="No drops found.")
    except Exception as e:
        logger.error(f"Can't get list of dropper contracts end with error: {e}")
        raise DropperHTTPException(status_code=500, detail="Can't get contracts")

    response = [
        data.DropperContractResponse(
            id=result.id,
            blockchain=result.blockchain,
            address=result.address,
            title=result.title,
            description=result.description,
            image_uri=result.image_uri,
        )
        for result in results
    ]

    return response


@app.get("/drops/{dropper_claim_id}", response_model=data.DropperClaimResponse)
async def get_drop_handler(
    request: Request,
    dropper_claim_id: str,
    db_session: Session = Depends(db.yield_db_session),
) -> data.DropperClaimResponse:
    """
    Get drop.
    """

    try:
        drop = actions.get_drop(
            db_session=db_session, dropper_claim_id=dropper_claim_id
        )
    except NoResultFound:
        raise DropperHTTPException(status_code=404, detail="No drops found.")
    except Exception as e:
        logger.error(f"Can't get drop {dropper_claim_id} end with error: {e}")
        raise DropperHTTPException(status_code=500, detail="Can't get drop")

    # if drop.terminus_address is not None and drop.terminus_pool_id is not None:
    #     try:
    #         actions.ensure_admin_token_holder(
    #             db_session, dropper_claim_id, request.state.address
    #         )
    #     except actions.AuthorizationError as e:
    #         logger.error(e)
    #         raise DropperHTTPException(status_code=403)
    #     except NoResultFound:
    #         raise DropperHTTPException(status_code=404, detail="Drop not found")

    return data.DropperClaimResponse(
        id=drop.id,
        dropper_contract_id=drop.dropper_contract_id,
        title=drop.title,
        description=drop.description,
        active=drop.active,
        claim_block_deadline=drop.claim_block_deadline,
        terminus_address=drop.terminus_address,
        terminus_pool_id=drop.terminus_pool_id,
        claim_id=drop.claim_id,
    )


@app.get("/terminus")
async def get_drops_terminus_handler(
    blockchain: str = Query(None),
    db_session: Session = Depends(db.yield_db_session),
) -> List[data.DropperTerminusResponse]:

    """
    Return distinct terminus pools
    """

    try:
        results = actions.list_drops_terminus(
            db_session=db_session, blockchain=blockchain
        )
    except Exception as e:
        logger.error(f"Can't get list of terminus contracts end with error: {e}")
        raise DropperHTTPException(
            status_code=500, detail="Can't get terminus contracts"
        )

    response = [
        data.DropperTerminusResponse(
            terminus_address=result.terminus_address,
            terminus_pool_id=result.terminus_pool_id,
            blockchain=result.blockchain,
        )
        for result in results
    ]

    return response
