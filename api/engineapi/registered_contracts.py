import argparse
from enum import Enum
import json
import logging
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from web3 import Web3

from . import db
from . import data
from .models import (
    RegisteredContract,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContractType(Enum):
    raw = "raw"
    dropper = "dropper-v0.2.0"


def register_contract(
    db_session: Session,
    blockchain: str,
    address: str,
    contract_type: str,
    moonstream_user_id: uuid.UUID,
    title: Optional[str],
    description: Optional[str],
    image_uri: Optional[str],
) -> uuid.UUID:
    """
    Register a contract against the Engine instance
    """

    contract = RegisteredContract(
        blockchain=blockchain,
        address=Web3.toChecksumAddress(address),
        contract_type=contract_type,
        moonstream_user_id=moonstream_user_id,
        title=title,
        description=description,
        image_uri=image_uri,
    )
    db_session.add(contract)
    db_session.commit()
    return contract.id


def lookup_registered_contracts(
    db_session: Session,
    moonstream_user_id: uuid.UUID,
    blockchain: Optional[str] = None,
    address: Optional[str] = None,
    contract_type: Optional[str] = None,
    limit: int = 10,
    offset: Optional[int] = None,
) -> RegisteredContract:
    """
    Lookup a registered contract
    """
    query = db_session.query(RegisteredContract).filter(
        RegisteredContract.moonstream_user_id == moonstream_user_id
    )

    if blockchain is not None:
        query = query.filter(RegisteredContract.blockchain == blockchain)

    if address is not None:
        query = query.filter(
            RegisteredContract.address == Web3.toChecksumAddress(address)
        )

    if contract_type is not None:
        query = query.filter(RegisteredContract.contract_type == contract_type)

    if offset is not None:
        query = query.offset(offset)

    query = query.limit(limit)

    return query.all()


def delete_registered_contract(
    db_session: Session,
    moonstream_user_id: uuid.UUID,
    registered_contract_id: uuid.UUID,
) -> RegisteredContract:
    """
    Delete a registered contract
    """
    registered_contract = (
        db_session.query(RegisteredContract)
        .filter(RegisteredContract.moonstream_user_id == moonstream_user_id)
        .filter(RegisteredContract.id == registered_contract_id)
        .one()
    )

    db_session.delete(registered_contract)
    db_session.commit()

    return registered_contract


def render_registered_contract(contract: RegisteredContract) -> data.RegisteredContract:
    return data.RegisteredContract(
        id=contract.id,
        blockchain=contract.blockchain,
        address=contract.address,
        contract_type=contract.contract_type,
        moonstream_user_id=contract.moonstream_user_id,
        title=contract.title,
        description=contract.description,
        image_uri=contract.image_uri,
    )


def handle_register(args: argparse.Namespace) -> None:
    """
    Handles the register command.
    """
    try:
        with db.yield_db_session_ctx() as db_session:
            contract = register_contract(
                db_session=db_session,
                blockchain=args.blockchain,
                address=args.address,
                contract_type=args.contract_type.value,
                moonstream_user_id=args.user_id,
                title=args.title,
                description=args.description,
                image_uri=args.image_uri,
            )
    except Exception as err:
        logger.error(err)
        return
    print(contract)


def handle_list(args: argparse.Namespace) -> None:
    """
    Handles the list command.
    """
    try:
        with db.yield_db_session_ctx() as db_session:
            contracts = lookup_registered_contracts(
                db_session=db_session,
                moonstream_user_id=args.user_id,
                blockchain=args.blockchain,
                address=args.address,
                contract_type=(
                    args.contract_type.value if args.contract_type is not None else None
                ),
                limit=args.limit,
                offset=args.offset,
            )
    except Exception as err:
        logger.error(err)
        return

    print(
        json.dumps(
            [render_registered_contract(contract).dict() for contract in contracts]
        )
    )


def handle_delete(args: argparse.Namespace) -> None:
    """
    Handles the delete command.
    """
    try:
        with db.yield_db_session_ctx() as db_session:
            deleted_contract = delete_registered_contract(
                db_session=db_session,
                registered_contract_id=args.id,
                moonstream_user_id=args.user_id,
            )
    except Exception as err:
        logger.error(err)
        return

    print(render_registered_contract(deleted_contract))


def generate_cli() -> argparse.ArgumentParser:
    """
    Generates a CLI which can be used to manage registered contracts on an Engine instance.
    """
    parser = argparse.ArgumentParser(description="Manage registered contracts")
    parser.set_defaults(func=lambda _: parser.print_help())
    subparsers = parser.add_subparsers()

    register_usage = "Register a new contract"
    register_parser = subparsers.add_parser(
        "register", help=register_usage, description=register_usage
    )
    # Copilot, generate register_parser all the way, please.
    register_parser.add_argument(
        "-b",
        "--blockchain",
        type=str,
        required=True,
        help="The blockchain the contract is deployed on",
    )
    register_parser.add_argument(
        "-a",
        "--address",
        type=str,
        required=True,
        help="The address of the contract",
    )
    register_parser.add_argument(
        "-c",
        "--contract-type",
        type=ContractType,
        choices=ContractType,
        required=True,
        help="The type of the contract",
    )
    register_parser.add_argument(
        "-u",
        "--user-id",
        type=uuid.UUID,
        required=True,
        help="The ID of the Moonstream user under whom to register the contract",
    )
    register_parser.add_argument(
        "-t",
        "--title",
        type=str,
        required=False,
        default=None,
        help="The title of the contract",
    )
    register_parser.add_argument(
        "-d",
        "--description",
        type=str,
        required=False,
        default=None,
        help="The description of the contract",
    )
    register_parser.add_argument(
        "-i",
        "--image-uri",
        type=str,
        required=False,
        default=None,
        help="The image URI of the contract",
    )
    register_parser.set_defaults(func=handle_register)

    list_usage = "List all contracts matching certain criteria"
    list_parser = subparsers.add_parser("list", help=list_usage, description=list_usage)
    list_parser.add_argument(
        "-b",
        "--blockchain",
        type=str,
        required=False,
        default=None,
        help="The blockchain the contract is deployed on",
    )
    list_parser.add_argument(
        "-a",
        "--address",
        type=str,
        required=False,
        default=None,
        help="The address of the contract",
    )
    list_parser.add_argument(
        "-c",
        "--contract-type",
        type=ContractType,
        choices=ContractType,
        required=False,
        default=None,
        help="The type of the contract",
    )
    list_parser.add_argument(
        "-u",
        "--user-id",
        type=uuid.UUID,
        required=True,
        help="The ID of the Moonstream user whose contracts to list",
    )
    list_parser.add_argument(
        "-N",
        "--limit",
        type=int,
        required=False,
        default=1,
        help="The number of contracts to return",
    )
    list_parser.add_argument(
        "-o",
        "--offset",
        type=int,
        required=False,
        default=0,
        help="The offset to start returning contracts from",
    )
    list_parser.set_defaults(func=handle_list)

    delete_usage = "Delete a registered contract from an Engine instance"
    delete_parser = subparsers.add_parser(
        "delete", help=delete_usage, description=delete_usage
    )
    delete_parser.add_argument(
        "--id",
        type=uuid.UUID,
        required=True,
        help="The ID of the contract to delete",
    )
    delete_parser.add_argument(
        "-u",
        "--user-id",
        type=uuid.UUID,
        required=True,
        help="The ID of the Moonstream user whose contract to delete",
    )
    delete_parser.set_defaults(func=handle_delete)

    return parser


def main() -> None:
    parser = generate_cli()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
