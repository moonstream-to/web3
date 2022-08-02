from datetime import datetime
from typing import List, Any, Optional, Dict
import uuid
import logging

from brownie import network, web3
from eth_typing import Address
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import percentile_disc
from sqlalchemy import func, text, or_
from web3 import Web3
from web3.types import ChecksumAddress

from engineapi.Dropper import Dropper


from . import Dropper, MockErc20, MockTerminus
from .models import (
    DropperClaimant,
    DropperContract,
    DropperClaim,
    Leaderboard,
    LeaderboardScores,
)
from . import signatures
from .settings import BLOCKCHAINS_TO_BROWNIE_NETWORKS


class AuthorizationError(Exception):
    pass


class DropWithNotSettedBlockDeadline(Exception):
    pass

class DublicateClaimantError(Exception):
    pass


BATCH_SIGNATURE_PAGE_SIZE = 500

logger = logging.getLogger(__name__)


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
    dropper_contract_id: uuid.UUID,
    claim_id: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    terminus_address: Optional[ChecksumAddress] = None,
    terminus_pool_id: Optional[int] = None,
    claim_block_deadline: Optional[int] = None,
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


def activate_drop(db_session: Session, dropper_claim_id: uuid.UUID):
    """
    Activate a claim
    """

    claim = (
        db_session.query(DropperClaim).filter(DropperClaim.id == dropper_claim_id).one()
    )

    claim.active = True
    db_session.commit()

    return claim


def deactivate_drop(db_session: Session, dropper_claim_id: uuid.UUID):
    """
    Activate a claim
    """

    claim = (
        db_session.query(DropperClaim).filter(DropperClaim.id == dropper_claim_id).one()
    )

    claim.active = False
    db_session.commit()

    return claim


def update_drop(
    db_session: Session,
    dropper_claim_id: uuid.UUID,
    title: Optional[str] = None,
    description: Optional[str] = None,
    terminus_address: Optional[str] = None,
    terminus_pool_id: Optional[int] = None,
    claim_block_deadline: Optional[int] = None,
    claim_id: Optional[int] = None,
    address: Optional[str] = None,
):
    """
    Update a claim
    """

    claim = (
        db_session.query(DropperClaim).filter(DropperClaim.id == dropper_claim_id).one()
    )

    if title:
        claim.title = title
    if description:
        claim.description = description
    if terminus_address or terminus_pool_id:
        ensure_dropper_contract_owner(db_session, claim.dropper_contract_id, address)
        if terminus_address:
            terminus_address = Web3.toChecksumAddress(terminus_address)
            claim.terminus_address = terminus_address
        if terminus_pool_id:
            claim.terminus_pool_id = terminus_pool_id
    if claim_block_deadline:
        claim.claim_block_deadline = claim_block_deadline
    if claim_id:
        claim.claim_id = claim_id

    db_session.commit()

    return claim


def get_free_drop_number_in_range(db_session: Session, dropper_contract_id: uuid.UUID, start: Optional[int], end: int):
    """
    Return list of free drops number in range
    """

    if start is None:
        start = 0

    drops = (
        db_session.query(DropperClaim)
        .filter(DropperClaim.dropper_contract_id == dropper_contract_id)
        .filter(DropperClaim.claim_id >= start)
        .filter(DropperClaim.claim_id <= end)
        .all()
    )
    free_numbers = list(range(start, end + 1))
    for drop in drops:
        free_numbers.remove(drop.claim_id)
    return drops


def add_claimants(db_session: Session, dropper_claim_id, claimants, added_by):
    """
    Add a claimants to a claim
    """

    # On conflict requirements https://stackoverflow.com/questions/42022362/no-unique-or-exclusion-constraint-matching-the-on-conflict

    claimant_objects = []

    addresses = [Web3.toChecksumAddress(claimant.address) for claimant in claimants]

    if len(claimants) > len(set(addresses)):
        raise DublicateClaimantError("Duplicate claimants")

    for claimant in claimants:
        claimant_objects.append(
            {
                "dropper_claim_id": dropper_claim_id,
                "address": Web3.toChecksumAddress(claimant.address),
                "amount": 0,
                "raw_amount": str(claimant.amount),
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
            raw_amount=insert_statement.excluded.raw_amount,
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
    decimals = int(erc20_contract.decimals())

    return db_amount * (10**decimals)


def batch_transform_claim_amounts(
    db_session: Session, dropper_claim_id: uuid.UUID, db_amounts: List[int]
) -> List[int]:
    claim = (
        db_session.query(DropperClaim.claim_id, DropperContract.address)
        .join(DropperContract, DropperContract.id == DropperClaim.dropper_contract_id)
        .filter(DropperClaim.id == dropper_claim_id)
        .one()
    )
    dropper_contract = Dropper.Dropper(claim.address)
    claim_info = dropper_contract.get_claim(claim.claim_id)
    if claim_info[0] != 20:
        return db_amounts

    erc20_contract = MockErc20.MockErc20(claim_info[1])
    decimals = int(erc20_contract.decimals())

    return [db_amount * (10**decimals) for db_amount in db_amounts]


def get_claimants(
    db_session: Session,
    dropper_claim_id: uuid.UUID,
    amount: Optional[int] = None,
    added_by: Optional[str] = None,
    address: Optional[ChecksumAddress] = None,
    limit=None,
    offset=None,
):
    """
    Search for a claimant by address
    """
    claimants_query = db_session.query(
        DropperClaimant.address,
        DropperClaimant.amount,
        DropperClaimant.added_by,
        DropperClaimant.raw_amount,
    ).filter(DropperClaimant.dropper_claim_id == dropper_claim_id)

    if amount:
        claimants_query = claimants_query.filter(DropperClaimant.amount == amount)
    if added_by:
        claimants_query = claimants_query.filter(DropperClaimant.added_by == added_by)
    if address:
        claimants_query = claimants_query.filter(DropperClaimant.address == address)

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
            DropperClaimant.id.label("dropper_claimant_id"),
            DropperClaimant.address,
            DropperClaimant.amount,
            DropperClaimant.raw_amount,
            DropperClaimant.signature,
            DropperClaim.id.label("dropper_claim_id"),
            DropperClaim.claim_id,
            DropperClaim.active,
            DropperClaim.claim_block_deadline,
            DropperClaim.title,
            DropperClaim.description,
            DropperContract.address.label("dropper_contract_address"),
            (DropperClaim.updated_at < DropperClaimant.updated_at).label(
                "is_recent_signature"
            ),
        )
        .join(DropperClaim, DropperClaimant.dropper_claim_id == DropperClaim.id)
        .join(DropperContract, DropperClaim.dropper_contract_id == DropperContract.id)
        .filter(DropperClaimant.dropper_claim_id == dropper_claim_id)
        .filter(DropperClaimant.address == Web3.toChecksumAddress(address))
    )

    return claimant_query.one()


def get_claimant_drops(
    db_session: Session,
    blockchain: str,
    address,
    current_block_number=None,
    limit=None,
    offset=None,
):
    """
    Search for a claimant by address
    """

    claimant_query = (
        db_session.query(
            DropperClaimant.id.label("dropper_claimant_id"),
            DropperClaimant.address,
            DropperClaimant.amount,
            DropperClaimant.raw_amount,
            DropperClaimant.signature,
            DropperClaim.id.label("dropper_claim_id"),
            DropperClaim.claim_id,
            DropperClaim.active,
            DropperClaim.claim_block_deadline,
            DropperClaim.title,
            DropperClaim.description,
            DropperContract.address.label("dropper_contract_address"),
            DropperContract.blockchain,
            (DropperClaim.updated_at < DropperClaimant.updated_at).label(
                "is_recent_signature"
            ),
        )
        .join(DropperClaim, DropperClaimant.dropper_claim_id == DropperClaim.id)
        .join(DropperContract, DropperClaim.dropper_contract_id == DropperContract.id)
        .filter(DropperClaim.active == True)
        .filter(DropperClaimant.address == address)
        .filter(DropperContract.blockchain == blockchain)
    )

    if current_block_number:
        logger.info("Trying to filter block number " + str(current_block_number))
        claimant_query = claimant_query.filter(
            DropperClaim.claim_block_deadline > current_block_number
        )

    claimant_query.order_by(DropperClaimant.created_at.asc())

    if limit:
        claimant_query = claimant_query.limit(limit)

    if offset:
        claimant_query = claimant_query.offset(offset)

    return claimant_query.all()


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


def get_drop(db_session: Session, dropper_claim_id: uuid.UUID):
    """
    Return particular drop
    """
    drop = (
        db_session.query(DropperClaim).filter(DropperClaim.id == dropper_claim_id).one()
    )
    return drop


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


def get_drops(
    db_session: Session,
    blockchain: str,
    dropper_contract_address: Optional[ChecksumAddress] = None,
    drop_number: Optional[int] = None,
    terminus_address: Optional[ChecksumAddress] = None,
    terminus_pool_id: Optional[int] = None,
    active: Optional[bool] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
):
    """
    Get drops
    """

    query = (
        db_session.query(
            DropperClaim.id,
            DropperClaim.title,
            DropperClaim.description,
            DropperClaim.terminus_address,
            DropperClaim.terminus_pool_id,
            DropperClaim.claim_block_deadline,
            DropperClaim.claim_id.label("drop_number"),
            DropperClaim.active,
            DropperContract.address.label("dropper_contract_address"),
        )
        .join(DropperContract)
        .filter(DropperContract.blockchain == blockchain)
    )

    if dropper_contract_address:
        query = query.filter(DropperContract.address == dropper_contract_address)

    if drop_number:
        query = query.filter(DropperClaim.claim_id == drop_number)

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


def ensure_contract_admin_token_holder(
    blockchain: str,
    dropper_contract_address: ChecksumAddress,
    address: ChecksumAddress,
) -> bool:
    brownie_network = BLOCKCHAINS_TO_BROWNIE_NETWORKS.get(blockchain)
    if brownie_network is None:
        raise ValueError(f"No brownie network for blockchain: {blockchain}")

    try:
        network.connect(brownie_network)
    except Exception:
        pass
    dropper = Dropper.Dropper(dropper_contract_address)

    terminus_address, terminus_pool_id = None  # dropper.get_terminus
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


def refetch_drop_signatures(
    db_session: Session, dropper_claim_id: uuid.UUID, added_by: str
):
    """
    Refetch signatures for drop
    """

    claim = (
        db_session.query(
            DropperClaim.claim_id,
            DropperClaim.claim_block_deadline,
            DropperContract.address,
        )
        .join(DropperContract, DropperClaim.dropper_contract_id == DropperContract.id)
        .filter(DropperClaim.id == dropper_claim_id)
    ).one()

    if claim.claim_block_deadline is None:
        raise DropWithNotSettedBlockDeadline(
            f"Claim block deadline is not set for dropper claim: {dropper_claim_id}"
        )

    outdated_signatures = (
        db_session.query(
            DropperClaim.claim_id,
            DropperClaimant.address,
            DropperClaimant.amount,
        )
        .join(DropperClaimant, DropperClaimant.dropper_claim_id == DropperClaim.id)
        .filter(DropperClaim.id == dropper_claim_id)
        .filter(
            or_(
                DropperClaimant.updated_at < DropperClaim.updated_at,
                DropperClaimant.signature == None,
            )
        )
    ).limit(BATCH_SIGNATURE_PAGE_SIZE)

    current_offset = 0

    users_hashes = {}
    users_amount = {}
    hashes_signature = {}

    dropper_contract = Dropper.Dropper(claim.address)

    while True:
        signature_requests = []

        page = outdated_signatures.offset(current_offset).all()

        claim_amounts = [outdated_signature.amount for outdated_signature in page]

        transformed_claim_amounts = batch_transform_claim_amounts(
            db_session, dropper_claim_id, claim_amounts
        )

        for outdated_signature, transformed_claim_amount in zip(
            page, transformed_claim_amounts
        ):

            message_hash_raw = dropper_contract.claim_message_hash(
                claim.claim_id,
                outdated_signature.address,
                claim.claim_block_deadline,
                transformed_claim_amount,
            )
            message_hash = str(message_hash_raw)
            signature_requests.append(message_hash)
            users_hashes[outdated_signature.address] = message_hash
            users_amount[outdated_signature.address] = outdated_signature.amount

        message_hashes = [signature_request for signature_request in signature_requests]

        signed_messages = signatures.DROP_SIGNER.batch_sign_message(message_hashes)

        hashes_signature.update(signed_messages)

        if len(page) == 0:
            break

        current_offset += BATCH_SIGNATURE_PAGE_SIZE

    claimant_objects = []

    for address, hash in users_hashes.items():
        claimant_objects.append(
            {
                "dropper_claim_id": dropper_claim_id,
                "address": address,
                "signature": hashes_signature[hash],
                "amount": users_amount[address],
                "added_by": added_by,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        )

    insert_statement = insert(DropperClaimant).values(claimant_objects)

    result_stmt = insert_statement.on_conflict_do_update(
        index_elements=[DropperClaimant.address, DropperClaimant.dropper_claim_id],
        set_=dict(
            signature=insert_statement.excluded.signature,
            updated_at=datetime.now(),
        ),
    )
    db_session.execute(result_stmt)
    db_session.commit()

    return claimant_objects


def get_leaderboard_total_count(db_session: Session, leaderboard_id):
    """
    Get the total number of claimants in the leaderboard
    """
    return (
        db_session.query(LeaderboardScores)
        .filter(LeaderboardScores.leaderboard_id == leaderboard_id)
        .count()
    )


def get_position(
    db_session: Session, leaderboard_id, address, window_size, limit: int, offset: int
):
    """

    Return position by address with window size
    """
    query = db_session.query(
        LeaderboardScores.address,
        LeaderboardScores.score,
        LeaderboardScores.points_data.label("points_data"),
        func.rank().over(order_by=LeaderboardScores.score.desc()).label("rank"),
        func.row_number().over(order_by=LeaderboardScores.score.desc()).label("number"),
    ).filter(LeaderboardScores.leaderboard_id == leaderboard_id)

    ranked_leaderboard = query.cte(name="ranked_leaderboard")

    query = db_session.query(
        ranked_leaderboard.c.address,
        ranked_leaderboard.c.score,
        ranked_leaderboard.c.rank,
        ranked_leaderboard.c.number,
    ).filter(
        ranked_leaderboard.c.address == address,
    )

    my_position = query.cte(name="my_position")

    # get the position with the window size

    query = db_session.query(
        ranked_leaderboard.c.address,
        ranked_leaderboard.c.score,
        ranked_leaderboard.c.rank,
        ranked_leaderboard.c.number,
        ranked_leaderboard.c.points_data,
    ).filter(
        ranked_leaderboard.c.number.between(  # taking off my hat!
            my_position.c.number - window_size,
            my_position.c.number + window_size,
        )
    )

    if limit:
        query = query.limit(limit)

    if offset:
        query = query.offset(offset)

    return query.all()


def get_leaderboard_positions(
    db_session: Session, leaderboard_id, limit: int, offset: int
):
    """
    Get the leaderboard positions
    """
    query = (
        db_session.query(
            LeaderboardScores.address,
            LeaderboardScores.score,
            LeaderboardScores.points_data,
            func.rank().over(order_by=LeaderboardScores.score.desc()).label("rank"),
        )
        .filter(LeaderboardScores.leaderboard_id == leaderboard_id)
        .order_by(text("rank asc"))
    )

    if limit:
        query = query.limit(limit)

    if offset:
        query = query.offset(offset)

    return query.all()


def get_qurtiles(db_session: Session, leaderboard_id):
    """
    Get the leaderboard qurtiles
    https://docs.sqlalchemy.org/en/14/core/functions.html#sqlalchemy.sql.functions.percentile_disc
    """

    query = db_session.query(
        LeaderboardScores.address,
        LeaderboardScores.score,
        func.rank().over(order_by=LeaderboardScores.score.desc()).label("rank"),
    ).filter(LeaderboardScores.leaderboard_id == leaderboard_id)

    ranked_leaderboard = query.cte(name="ranked_leaderboard")

    current_count = db_session.query(ranked_leaderboard).count()

    index_75 = int(current_count / 4)

    index_50 = int(current_count / 2)

    index_25 = int(current_count * 3 / 4)

    q1 = db_session.query(ranked_leaderboard).limit(1).offset(index_25).first()

    q2 = db_session.query(ranked_leaderboard).limit(1).offset(index_50).first()

    q3 = db_session.query(ranked_leaderboard).limit(1).offset(index_75).first()

    return q1, q2, q3


def create_leaderboard(db_session: Session, title: str, description: str):
    """
    Create a leaderboard
    """

    leaderboard = Leaderboard(title=title, description=description)
    db_session.add(leaderboard)
    db_session.commit()

    return leaderboard.id


def get_leaderboard_by_id(db_session: Session, leaderboard_id):
    """
    Get the leaderboard by id
    """
    return db_session.query(Leaderboard).filter(Leaderboard.id == leaderboard_id).one()


def get_leaderboard_by_title(db_session: Session, title):
    """
    Get the leaderboard by title
    """
    return db_session.query(Leaderboard).filter(Leaderboard.title == title).one()


def list_leaderboards(db_session: Session, limit: int, offset: int):
    """
    List all leaderboards
    """
    query = db_session.query(Leaderboard.id, Leaderboard.title, Leaderboard.description)

    if limit:
        query = query.limit(limit)

    if offset:
        query = query.offset(offset)

    return query.all()


def add_scores(db_session: Session, leaderboard_id, scores):
    """
    Add scores to the leaderboard
    """

    leaderboard_scores = []

    for score in scores:
        leaderboard_scores.append(
            {
                "leaderboard_id": leaderboard_id,
                "address": score["address"],
                "score": score["score"],
                "points_data": score["points_data"],
            }
        )

    insert_statement = insert(LeaderboardScores).values(leaderboard_scores)

    result_stmt = insert_statement.on_conflict_do_update(
        index_elements=[LeaderboardScores.address, LeaderboardScores.leaderboard_id],
        set_=dict(
            score=insert_statement.excluded.score,
            points_data=insert_statement.excluded.points_data,
            updated_at=datetime.now(),
        ),
    )
    db_session.execute(result_stmt)
    db_session.commit()

    return leaderboard_scores
