from .models import Claimant, DropperContract, DropperClaim, ClaimantClaim, Claimant


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

    dropper_claim = DropperClaim(
        dropper_contract_id=dropper_contract_id,
        claim_id=claim_id,
        title=title,
        description=description,
        terminus_address=terminus_address,
        terminus_pool_id=terminus_pool_id,
        claim_block_deadline=claim_block_deadline,
    )
    db_session.add(dropper_claim)
    db_session.commit()
    return dropper_claim


def add_claimant(db_session, dropper_claim_id, claimants):
    """
    Add a claimants to a claim
    """

    for claimant in claimants:
        claimant = Claimant(
            dropper_claim_id=dropper_claim_id,
            address=claimant.address,
            amount=claimant.amount,
            added_by=claimant.added_by,
        )
        db_session.add(claimant)

    db_session.commit()

    return claimants


def get_claimant(db_session, dropper_claim_id, address):
    """
    Search for a claimant by address
    """

    claimants = (
        db_session.query(Claimant.address, Claimant.amount, DropperClaim.claim_id)
        .join(DropperClaim)
        .filter(Claimant.dropper_claim_id == dropper_claim_id)
        .filter(Claimant.address == address)
        .all()
    )

    return claimants


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
