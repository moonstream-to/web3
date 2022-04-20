import re
from .models import Claimant, DropperContract, DropperClaim, Claimant

import web3


def create_dropper_contract(db_session, blockchain, dropper_contract_address):
    """
    Create a new dropper contract.
    """

    dropper_contract = DropperContract(
        blockchain=blockchain, address=dropper_contract_address
    )
    db_session.add(dropper_contract)
    db_session.commit()
    return dropper_contract


def create_claim(
    db_session,
    dropper_contract_address,
    blockchain,
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
        .filter(DropperContract.address == dropper_contract_address)
        .filter(DropperContract.blockchain == blockchain)
        .one_or_none()
    )

    if dropper_contract is None:
        dropper_contract = create_dropper_contract(dropper_contract_address, blockchain)

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


def add_claimants(db_session, dropper_claim_id, claimants):
    """
    Add a claimants to a claim
    """

    # get the claimamants for this dropper claim

    claimants_for_claim = get_claimants(db_session, dropper_claim_id)

    already_added = [address for address, _, _ in claimants_for_claim]

    for claimant in claimants:
        if claimant.address not in already_added:
            claimant_claim = DropperClaim(
                dropper_claim_id=dropper_claim_id,
                address=web3.toChecksumAddress(claimant.address),
                amount=claimant.amount,
                added_by=claimant.added_by,
            )
            db_session.add(claimant_claim)
            db_session.commit()
            db_session.refresh(claimant_claim)  # refresh the object to get the id
            already_added.append(claimant.address)
    return claimants


def get_claimants(db_session, dropper_claim_id, address=None):
    """
    Search for a claimant by address
    """

    claimants_query = (
        db_session.query(Claimant.address, Claimant.amount, DropperClaim.claim_id)
        .join(DropperClaim)
        .filter(Claimant.dropper_claim_id == dropper_claim_id)
    )

    if address is not None:
        claimants_query = claimants_query.filter(Claimant.address == address)

    return claimants_query.all()


def get_claims(db_session, dropper_contract_id, blockchain, address):
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
            Claimant.address,
            Claimant.amount,
            Claimant.added_by,
        )
        .join(DropperContract)
        .join(Claimant)
        .filter(DropperClaim.dropper_contract_id == dropper_contract_id)
        .filter(DropperContract.blockchain == blockchain)
        .filter(Claimant.address == address)
        .all()
    )

    return claims


def delete_claimants(db_session, dropper_claim_id, addresses):
    """
    Delete all claimants for a claim
    """

    normalize_addresses = [web3.toChecksumAddress(address) for address in addresses]

    deleted_addresses = (
        db_session.delete(Claimant)
        .filter(Claimant.dropper_claim_id == dropper_claim_id)
        .filter(Claimant.address.in_(normalize_addresses))
    )
    db_session.commit()

    return deleted_addresses
