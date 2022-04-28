from datetime import datetime
from typing import List, Any, Optional, Dict, cast
import uuid

from brownie import network
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from web3 import Web3
from web3.types import ChecksumAddress

from lootbox.Dropper import Dropper

from . import Dropper, MockErc20, MockTerminus
from .models import DropperClaimant, DropperContract, DropperClaim
from .settings import BLOCKCHAINS_TO_BROWNIE_NETWORKS


class AuthorizationError(Exception):
    pass


def create_dropper_contract(
    db_session: Session,
    blockchain: Optional[str],
    dropper_contract_address,
    title,
    description,
    image_uri,
):
    """
    Create a new dropper contract.
    """

    dropper_contract = DropperContract(
        blockchain=blockchain,
        address=Web3.toChecksumAddress(dropper_contract_address),
        title=title,
        description=description,
        image_uri=image_uri,
    )
    db_session.add(dropper_contract)
    db_session.commit()
    return dropper_contract


def delete_dropper_contract(
    db_session: Session, blockchain: Optional[str], dropper_contract_address
):

    dropper_contract = (
        db_session.query(DropperContract)
        .filter(
            DropperContract.address == Web3.toChecksumAddress(dropper_contract_address)
        )
        .filter(DropperContract.blockchain == blockchain)
        .one()
    )

    db_session.delete(dropper_contract)
    db_session.commit()
    return dropper_contract


def list_dropper_contracts(
    db_session: Session, blockchain: Optional[str]
) -> List[Dict[str, Any]]:
    """
    List all dropper contracts
    """

    dropper_contracts = []

    dropper_contracts = db_session.query(DropperContract)

    if blockchain:
        dropper_contracts = dropper_contracts.filter(
            DropperContract.blockchain == blockchain
        )

    return dropper_contracts


def get_dropper_contract_by_id(
    db_session: Session, dropper_contract_id: uuid.UUID
) -> DropperContract:
    """
    Get a dropper contract by its ID
    """
    query = db_session.query(DropperContract).filter(
        DropperContract.id == dropper_contract_id
    )
    return query.one()


def list_drops_terminus(db_session: Session, blockchain: Optional[str] = None):
    """
    List distinct of terminus addressess
    """

    terminus = (
        db_session.query(
            DropperClaim.terminus_address,
            DropperClaim.terminus_pool_id,
            DropperContract.blockchain,
        )
        .join(DropperContract)
        .filter(DropperClaim.terminus_address.isnot(None))
        .filter(DropperClaim.terminus_pool_id.isnot(None))
    )
    if blockchain:
        terminus = terminus.filter(DropperContract.blockchain == blockchain)

    terminus = terminus.distinct(
        DropperClaim.terminus_address, DropperClaim.terminus_pool_id
    )

    return terminus


def list_drops_blockchains(db_session: Session):
    """
    List distinct of blockchains
    """

    blockchains = (
        db_session.query(DropperContract.blockchain)
        .filter(DropperContract.blockchain.isnot(None))
        .distinct(DropperContract.blockchain)
    )

    return blockchains


def list_claims(db_session: Session, dropper_contract_id, active=True):
    """
    List all claims
    """

    claims = (
        db_session.query(
            DropperClaim.id,
            DropperClaim.title,
            DropperClaim.description,
            DropperClaim.terminus_address,
            DropperClaim.terminus_pool_id,
            DropperClaim.claim_block_deadline,
        )
        .filter(DropperClaim.dropper_contract_id == dropper_contract_id)
        .filter(DropperClaim.active == active)
        .all()
    )

    return claims


def delete_claim(db_session: Session, dropper_claim_id):
    """
    Delete a claim
    """

    claim = (
        db_session.query(DropperClaim).filter(DropperClaim.id == dropper_claim_id).one()
    )

    db_session.delete(claim)
    db_session.commit()

    return claim


def create_claim(
    db_session: Session,
    dropper_contract_id,
    claim_id,
    title,
    description,
    terminus_address,
    terminus_pool_id,
    claim_block_deadline,
):
    """
    Create a new dropper claim.
    """

    # get the dropper contract

    dropper_contract = (
        db_session.query(DropperContract)
        .filter(DropperContract.id == dropper_contract_id)
        .one()
    )

    dropper_claim = DropperClaim(
        dropper_contract_id=dropper_contract.id,
        claim_id=claim_id,
        title=title,
        description=description,
        terminus_address=terminus_address,
        terminus_pool_id=terminus_pool_id,
        claim_block_deadline=claim_block_deadline,
    )
    db_session.add(dropper_claim)
    db_session.commit()
    db_session.refresh(dropper_claim)  # refresh the object to get the id
    return dropper_claim


def add_claimants(db_session: Session, dropper_claim_id, claimants, added_by):
    """
    Add a claimants to a claim
    """

    # On conflict requirements https://stackoverflow.com/questions/42022362/no-unique-or-exclusion-constraint-matching-the-on-conflict

    claimant_objects = []

    for claimant in claimants:
        claimant_objects.append(
            {
                "dropper_claim_id": dropper_claim_id,
                "address": Web3.toChecksumAddress(claimant.address),
                "amount": claimant.amount,
                "added_by": added_by,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        )

    insert_statement = insert(DropperClaimant).values(claimant_objects)

    result_stmt = insert_statement.on_conflict_do_update(
        index_elements=[DropperClaimant.address, DropperClaimant.dropper_claim_id],
        set_=dict(
            amount=insert_statement.excluded.amount,
            added_by=insert_statement.excluded.added_by,
            updated_at=datetime.now(),
        ),
    )
    db_session.execute(result_stmt)
    db_session.commit()

    return claimant_objects


def transform_claim_amount(
    db_session: Session, dropper_claim_id: uuid.UUID, db_amount: int
) -> int:
    claim = (
        db_session.query(DropperClaim.claim_id, DropperContract.address)
        .join(DropperContract, DropperContract.id == DropperClaim.dropper_contract_id)
        .filter(DropperClaim.id == dropper_claim_id)
        .one()
    )
    dropper_contract = Dropper.Dropper(claim.address)
    claim_info = dropper_contract.get_claim(claim.claim_id)
    if claim_info[0] != 20:
        return db_amount

    erc20_contract = MockErc20.MockErc20(claim_info[1])
    decimals = cast(int, erc20_contract.decimals())

    return db_amount * decimals


def get_claimants(db_session: Session, dropper_claim_id, limit=None, offset=None):
    """
    Search for a claimant by address
    """
    claimants_query = db_session.query(
        DropperClaimant.address, DropperClaimant.amount, DropperClaimant.added_by
    ).filter(DropperClaimant.dropper_claim_id == dropper_claim_id)
    if limit:
        claimants_query = claimants_query.limit(limit)

    if offset:
        claimants_query = claimants_query.offset(offset)

    return claimants_query.all()


def get_claimant(db_session: Session, dropper_claim_id, address):
    """
    Search for a claimant by address
    """

    claimant_query = (
        db_session.query(
            DropperClaimant.address,
            DropperClaimant.amount,
            DropperClaim.id.label("dropper_claim_id"),
            DropperClaim.claim_id,
            DropperClaim.active,
            DropperClaim.claim_block_deadline,
            DropperContract.address.label("dropper_contract_address"),
        )
        .join(DropperClaim, DropperClaimant.dropper_claim_id == DropperClaim.id)
        .join(DropperContract, DropperClaim.dropper_contract_id == DropperContract.id)
        .filter(DropperClaimant.dropper_claim_id == dropper_claim_id)
        .filter(DropperClaimant.address == Web3.toChecksumAddress(address))
    )

    return claimant_query.one()


def get_terminus_claims(
    db_session: Session,
    blockchain: str,
    terminus_address: ChecksumAddress,
    terminus_pool_id: int,
    dropper_contract_address: Optional[ChecksumAddress] = None,
    active: Optional[bool] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
):
    """
    Search for a claimant by address
    """

    query = (
        db_session.query(
            DropperClaim.id,
            DropperClaim.title,
            DropperClaim.description,
            DropperClaim.terminus_address,
            DropperClaim.terminus_pool_id,
            DropperClaim.claim_block_deadline,
            DropperClaim.claim_id,
            DropperClaim.active,
            DropperContract.address.label("dropper_contract_address"),
        )
        .join(DropperContract)
        .filter(DropperClaim.terminus_address == terminus_address)
        .filter(DropperClaim.terminus_pool_id == terminus_pool_id)
        .filter(DropperContract.blockchain == blockchain)
    )

    if dropper_contract_address:
        query = query.filter(DropperContract.address == dropper_contract_address)

    if active:
        query = query.filter(DropperClaim.active == active)

    # TODO: add ordering in all pagination queries
    query = query.order_by(DropperClaim.created_at.asc())

    if limit:
        query = query.limit(limit)

    if offset:
        query = query.offset(offset)

    return query


def get_claims(
    db_session: Session,
    blockchain: str,
    dropper_contract_address: Optional[ChecksumAddress] = None,
    claimant_address: Optional[ChecksumAddress] = None,
    terminus_address: Optional[ChecksumAddress] = None,
    terminus_pool_id: Optional[int] = None,
    active: Optional[bool] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
):
    """
    Search for a claimant by address
    """

    query = (
        db_session.query(
            DropperClaim.id,
            DropperClaim.title,
            DropperClaim.description,
            DropperClaim.terminus_address,
            DropperClaim.terminus_pool_id,
            DropperClaim.claim_block_deadline,
            DropperClaim.claim_id,
            DropperClaim.active,
            DropperClaimant.amount,
            DropperContract.address.label("dropper_contract_address"),
        )
        .join(DropperContract)
        .join(DropperClaimant)
        .filter(DropperContract.blockchain == blockchain)
    )

    if dropper_contract_address:
        query = query.filter(DropperContract.address == dropper_contract_address)

    if claimant_address:
        query = query.filter(DropperClaimant.address == claimant_address)

    if terminus_address:
        query = query.filter(DropperClaim.terminus_address == terminus_address)

    if terminus_pool_id:
        query = query.filter(DropperClaim.terminus_pool_id == terminus_pool_id)

    if active:
        query = query.filter(DropperClaim.active == active)

    query = query.order_by(DropperClaim.created_at.asc())

    if limit:
        query = query.limit(limit)

    if offset:
        query = query.offset(offset)

    return query


def get_claim_admin_pool(
    db_session: Session,
    dropper_claim_id: uuid.UUID,
) -> Any:
    """
    Search for a claimant by address
    """

    query = (
        db_session.query(
            DropperContract.blockchain,
            DropperClaim.terminus_address,
            DropperClaim.terminus_pool_id,
        )
        .join(DropperContract)
        .filter(DropperClaim.id == dropper_claim_id)
    )
    return query.one()


def ensure_admin_token_holder(
    db_session: Session, dropper_claim_id: uuid.UUID, address: ChecksumAddress
) -> bool:
    blockchain, terminus_address, terminus_pool_id = get_claim_admin_pool(
        db_session=db_session, dropper_claim_id=dropper_claim_id
    )
    brownie_network = BLOCKCHAINS_TO_BROWNIE_NETWORKS.get(blockchain)
    if brownie_network is None:
        raise ValueError(f"No brownie network for blockchain: {blockchain}")

    try:
        network.connect(brownie_network)
    except Exception:
        pass
    terminus = MockTerminus.MockTerminus(terminus_address)
    balance = terminus.balance_of(address, terminus_pool_id)
    if balance == 0:
        raise AuthorizationError(
            f"Address has insufficient balance in Terminus pool: address={address}, blockchain={blockchain}, terminus_address={terminus_address}, terminus_pool_id={terminus_pool_id}"
        )
    return True


def ensure_dropper_contract_owner(
    db_session: Session, dropper_contract_id: uuid.UUID, address: ChecksumAddress
) -> bool:
    dropper_contract_info = get_dropper_contract_by_id(
        db_session=db_session, dropper_contract_id=dropper_contract_id
    )
    brownie_network = BLOCKCHAINS_TO_BROWNIE_NETWORKS.get(
        dropper_contract_info.blockchain
    )
    if brownie_network is None:
        raise ValueError(
            f"No brownie network for blockchain: {dropper_contract_info.blockchain}"
        )

    try:
        network.connect(brownie_network)
    except Exception:
        pass

    dropper = Dropper.Dropper(dropper_contract_info.address)
    dropper_owner_address = dropper.owner()
    if address != Web3.toChecksumAddress(dropper_owner_address):
        raise AuthorizationError(
            f"Given address is not the owner of the given dropper contract: address={address}, blockchain={dropper_contract_info.blockchain}, dropper_address={dropper_contract_info.address}"
        )
    return True


def delete_claimants(db_session: Session, dropper_claim_id, addresses):
    """
    Delete all claimants for a claim
    """

    normalize_addresses = [Web3.toChecksumAddress(address) for address in addresses]

    was_deleted = []
    deleted_addresses = (
        db_session.query(DropperClaimant)
        .filter(DropperClaimant.dropper_claim_id == dropper_claim_id)
        .filter(DropperClaimant.address.in_(normalize_addresses))
    )
    for deleted_address in deleted_addresses:
        was_deleted.append(deleted_address.address)
        db_session.delete(deleted_address)

    db_session.commit()

    return was_deleted
