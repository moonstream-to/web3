import argparse
from enum import Enum
import json
import logging

from .actions import (
    register_contract,
    lookup_registered_contracts,
    delete_registered_contract,
    render_registered_contract,
)
from . import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContractType(Enum):
    raw = "raw"
    dropper = "dropper-v0.2.0"


def handle_register_contract(args: argparse.Namespace) -> None:
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
                blockchain=args.blockchain,
                address=args.address,
                contract_type=args.contract_type.value
                if args.contract_type is not None
                else None,
                limit=args.limit,
                offset=args.offset,
            )
    except Exception as err:
        logger.error(err)
        return

    print(json.dumps([render_registered_contract(contract) for contract in contracts]))


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
    register_parser.set_defaults(func=handle_register_contract)

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

    return parser


def main() -> None:
    parser = generate_cli()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
