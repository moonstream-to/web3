from datetime import datetime
import re
from turtle import update

import sqlalchemy

from lootbox.drop import create_diff
from .models import DropperClaimant, DropperContract, DropperClaim
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import null as sql_null
from uuid import uuid4, UUID
from copy import deepcopy

from brownie import network, web3


def create_dropper_contract(db_session, blockchain, dropper_contract_address):
    """
    Create a new dropper contract.
    """

    dropper_contract = DropperContract(
        blockchain=blockchain,
        address=web3.toChecksumAddress(dropper_contract_address),
    )
    db_session.add(dropper_contract)
    db_session.commit()
    return dropper_contract


def delete_dropper_contract(db_session, blockchain, dropper_contract_address):

    dropper_contract = (
        db_session.query(DropperContract)
        .filter(DropperContract.address == dropper_contract_address)
        .filter(DropperContract.blockchain == blockchain)
        .one()
    )

    db_session.delete(dropper_contract)
    db_session.commit()
    return dropper_contract


def list_dropper_contracts(db_session, blockchain):
    """
    List all dropper contracts
    """

    dropper_contracts = []

    dropper_contracts = db_session.query(DropperContract).filter(
        DropperContract.blockchain == blockchain
    )

    return [(contract.id, contract.address) for contract in dropper_contracts]


def list_claims(db_session, dropper_contract_id, active=True):
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


def delete_claim(db_session, dropper_claim_id):
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
    db_session,
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


def add_claimants(db_session, dropper_claim_id, claimants, added_by):
    """
    Add a claimants to a claim
    """

    # On conflict requirements https://stackoverflow.com/questions/42022362/no-unique-or-exclusion-constraint-matching-the-on-conflict

    claimant_objects = []

    for claimant in claimants:
        claimant_objects.append(
            {
                "dropper_claim_id": dropper_claim_id,
                "address": web3.toChecksumAddress(claimant.address),
                "amount": claimant.amount,
                "added_by": added_by,
                "created_at": sql_null(),
                "updated_at": sql_null(),
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


def get_claimants(db_session, dropper_claim_id, limit=None, offset=None):
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


def get_claimant(db_session, dropper_claim_id, address):
    """
    Search for a claimant by address
    """

    claimant_query = (
        db_session.query(
            DropperClaimant.address,
            DropperClaimant.amount,
            DropperClaim.claim_id,
            DropperClaim.claim_block_deadline,
        )
        .join(DropperClaim)
        .filter(DropperClaimant.dropper_claim_id == dropper_claim_id)
        .filter(DropperClaimant.address == web3.toChecksumAddress(address))
        .filter(DropperClaim.claim_block_deadline > len(network.chain))
    )

    return claimant_query.one()


def get_claims(
    db_session,
    dropper_contract_id,
    blockchain,
    address,
    active,
    limit=None,
    offset=None,
):
    """
    Search for a claimant by address
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
        .join(DropperContract)
        .join(DropperClaimant)
        .filter(DropperClaim.dropper_contract_id == dropper_contract_id)
        .filter(DropperContract.blockchain == blockchain)
        .filter(DropperClaimant.address == address)
        .filter(DropperClaim.claim_block_deadline > len(network.chain))
        .filter(DropperClaim.active == active)
        .limit(limit)
        .offset(offset)
        .all()
    )

    return claims


def delete_claimants(db_session, dropper_claim_id, addresses):
    """
    Delete all claimants for a claim
    """

    normalize_addresses = [web3.toChecksumAddress(address) for address in addresses]

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
