import argparse
import json
import logging
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session
from web3 import Web3

from . import data, db
from .models import RegisteredContract, CallRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContractAlreadyRegistered(Exception):
    pass


class ContractType(Enum):
    raw = "raw"
    dropper = "dropper-v0.2.0"


def validate_method_and_params(
    contract_type: ContractType, method: str, parameters: Dict[str, Any]
) -> None:
    """
    Validate the given method and parameters for the specified contract_type.
    """
    if contract_type == ContractType.raw:
        if method != "":
            raise ValueError("Method must be empty string for raw contract type")
        if set(parameters.keys()) != {"calldata"}:
            raise ValueError(
                "Parameters must have only 'calldata' key for raw contract type"
            )
    elif contract_type == ContractType.dropper:
        if method != "claim":
            raise ValueError("Method must be 'claim' for dropper contract type")
        required_params = {
            "dropId",
            "requestID",
            "blockDeadline",
            "amount",
            "signer",
            "signature",
        }
        if set(parameters.keys()) != required_params:
            raise ValueError(
                f"Parameters must have {required_params} keys for dropper contract type"
            )


def register_contract(
    db_session: Session,
    blockchain: str,
    address: str,
    contract_type: ContractType,
    moonstream_user_id: uuid.UUID,
    title: Optional[str],
    description: Optional[str],
    image_uri: Optional[str],
) -> data.RegisteredContract:
    """
    Register a contract against the Engine instance
    """

    try:
        contract = RegisteredContract(
            blockchain=blockchain,
            address=Web3.toChecksumAddress(address),
            contract_type=contract_type.value,
            moonstream_user_id=moonstream_user_id,
            title=title,
            description=description,
            image_uri=image_uri,
        )
        db_session.add(contract)
        db_session.commit()
    except IntegrityError as err:
        db_session.rollback()
        raise ContractAlreadyRegistered()
    except Exception as err:
        db_session.rollback()
        logger.error(repr(err))
        raise

    return render_registered_contract(contract)


def lookup_registered_contracts(
    db_session: Session,
    moonstream_user_id: uuid.UUID,
    blockchain: Optional[str] = None,
    address: Optional[str] = None,
    contract_type: Optional[ContractType] = None,
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
        query = query.filter(RegisteredContract.contract_type == contract_type.value)

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
    try:
        registered_contract = (
            db_session.query(RegisteredContract)
            .filter(RegisteredContract.moonstream_user_id == moonstream_user_id)
            .filter(RegisteredContract.id == registered_contract_id)
            .one()
        )

        db_session.delete(registered_contract)
        db_session.commit()
    except Exception as err:
        db_session.rollback()
        logger.error(repr(err))
        raise

    return registered_contract


def request_calls(
    db_session: Session,
    moonstream_user_id: uuid.UUID,
    registered_contract_id: uuid.UUID,
    call_specs: List[data.CallSpecification],
    ttl_days: Optional[int] = None,
) -> None:
    """
    Batch creates call requests for the given registered contract.
    """
    # Check that ttl_days is positive (if specified)
    if ttl_days is not None and ttl_days <= 0:
        raise ValueError("ttl_days must be positive")

    # Check that the moonstream_user_id matches the RegisteredContract
    try:
        registered_contract = (
            db_session.query(RegisteredContract)
            .filter(
                RegisteredContract.id == registered_contract_id,
                RegisteredContract.moonstream_user_id == moonstream_user_id,
            )
            .one()
        )
    except NoResultFound:
        raise ValueError("Invalid registered_contract_id or moonstream_user_id")

    # Normalize the caller argument using Web3.toChecksumAddress
    contract_type = ContractType(registered_contract.contract_type)
    for specification in call_specs:
        normalized_caller = Web3.toChecksumAddress(specification.caller)

        # Validate the method and parameters for the contract_type
        validate_method_and_params(
            contract_type, specification.method, specification.parameters
        )

        # Calculate the expiration time (if ttl_days is specified)
        expires_at_sql = None
        if ttl_days is not None:
            expires_at_sql = text(f"(NOW() + INTERVAL '{ttl_days} days')")

        request = CallRequest(
            registered_contract_id=registered_contract.id,
            caller=normalized_caller,
            moonstream_user_id=moonstream_user_id,
            method=specification.method,
            parameters=specification.parameters,
            expires_at=expires_at_sql,
        )

        db_session.add(request)
    # Insert the new rows into the database in a single transaction
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e


def list_call_requests(
    db_session: Session,
    registered_contract_id: uuid.UUID,
    caller: str,
    limit: int = 10,
    offset: Optional[int] = None,
    show_expired: bool = False,
) -> List[data.CallRequest]:
    """
    List call requests for the given moonstream_user_id
    """
    # If show_expired is False, filter out expired requests using current time on database server
    query = db_session.query(CallRequest).filter(
        CallRequest.registered_contract_id == registered_contract_id,
        CallRequest.caller == Web3.toChecksumAddress(caller),
    )

    if not show_expired:
        query = query.filter(
            CallRequest.expires_at > func.now(),
        )

    if offset is not None:
        query = query.offset(offset)

    query = query.limit(limit)
    results = query.all()
    return [render_call_request(call_request) for call_request in results]


# TODO(zomglings): What should the delete functionality for call requests look like?
# - Delete expired requests for a given caller?
# - Delete all requests for a given caller?
# - Delete all requests for a given contract?
# - Delete request by ID?
# Should we implement these all using a single delete method, or a different method for each
# use case?
# Will come back to this once API is live.


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
        created_at=contract.created_at,
        updated_at=contract.updated_at,
    )


def render_call_request(call_request: CallRequest) -> data.CallRequest:
    return data.CallRequest(
        id=call_request.id,
        registered_contract_id=call_request.registered_contract_id,
        moonstream_user_id=call_request.moonstream_user_id,
        caller=call_request.caller,
        method=call_request.method,
        parameters=call_request.parameters,
        expires_at=call_request.expires_at,
        created_at=call_request.created_at,
        updated_at=call_request.updated_at,
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
                contract_type=args.contract_type,
                moonstream_user_id=args.user_id,
                title=args.title,
                description=args.description,
                image_uri=args.image_uri,
            )
    except Exception as err:
        logger.error(err)
        return
    print(contract.json())


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
                contract_type=args.contract_type,
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

    print(render_registered_contract(deleted_contract).json())


def handle_request_calls(args: argparse.Namespace) -> None:
    """
    Handles the request-calls command.

    Reads a file of JSON-formatted call specifications from `args.call_specs`,
    validates them, and adds them to the call_requests table in the Engine database.

    :param args: The arguments passed to the CLI command.
    """
    with args.call_specs as ifp:
        try:
            call_specs_raw = json.load(ifp)
        except Exception as e:
            logger.error(f"Failed to load call specs: {e}")
            return

        call_specs = [data.CallSpecification(**spec) for spec in call_specs_raw]

    try:
        with db.yield_db_session_ctx() as db_session:
            request_calls(
                db_session=db_session,
                moonstream_user_id=args.moonstream_user_id,
                registered_contract_id=args.registered_contract_id,
                call_specs=call_specs,
                ttl_days=args.ttl_days,
            )
    except Exception as e:
        logger.error(f"Failed to request calls: {e}")
        return


def handle_list_requests(args: argparse.Namespace) -> None:
    """
    Handles the requests command.

    :param args: The arguments passed to the CLI command.
    """
    try:
        with db.yield_db_session_ctx() as db_session:
            call_requests = list_call_requests(
                db_session=db_session,
                registered_contract_id=args.registered_contract_id,
                caller=args.caller,
                limit=args.limit,
                offset=args.offset,
                show_expired=args.show_expired,
            )
    except Exception as e:
        logger.error(f"Failed to list call requests: {e}")
        return

    print(json.dumps([request.dict() for request in call_requests]))


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

    list_contracts_usage = "List all contracts matching certain criteria"
    list_contracts_parser = subparsers.add_parser(
        "list", help=list_contracts_usage, description=list_contracts_usage
    )
    list_contracts_parser.add_argument(
        "-b",
        "--blockchain",
        type=str,
        required=False,
        default=None,
        help="The blockchain the contract is deployed on",
    )
    list_contracts_parser.add_argument(
        "-a",
        "--address",
        type=str,
        required=False,
        default=None,
        help="The address of the contract",
    )
    list_contracts_parser.add_argument(
        "-c",
        "--contract-type",
        type=ContractType,
        choices=ContractType,
        required=False,
        default=None,
        help="The type of the contract",
    )
    list_contracts_parser.add_argument(
        "-u",
        "--user-id",
        type=uuid.UUID,
        required=True,
        help="The ID of the Moonstream user whose contracts to list",
    )
    list_contracts_parser.add_argument(
        "-N",
        "--limit",
        type=int,
        required=False,
        default=10,
        help="The number of contracts to return",
    )
    list_contracts_parser.add_argument(
        "-n",
        "--offset",
        type=int,
        required=False,
        default=0,
        help="The offset to start returning contracts from",
    )
    list_contracts_parser.set_defaults(func=handle_list)

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

    request_calls_usage = "Create call requests for a registered contract"
    request_calls_parser = subparsers.add_parser(
        "request-calls", help=request_calls_usage, description=request_calls_usage
    )
    request_calls_parser.add_argument(
        "-i",
        "--registered-contract-id",
        type=uuid.UUID,
        required=True,
        help="The ID of the registered contract to create call requests for",
    )
    request_calls_parser.add_argument(
        "-u",
        "--moonstream-user-id",
        type=uuid.UUID,
        required=True,
        help="The ID of the Moonstream user who owns the contract",
    )
    request_calls_parser.add_argument(
        "-c",
        "--calls",
        type=argparse.FileType("r"),
        required=True,
        help="Path to the JSON file with call specifications",
    )
    request_calls_parser.add_argument(
        "-t",
        "--ttl-days",
        type=int,
        required=False,
        default=None,
        help="The number of days until the call requests expire",
    )
    request_calls_parser.set_defaults(func=handle_request_calls)

    list_requests_usage = "List requests for calls on a registered contract"
    list_requests_parser = subparsers.add_parser(
        "requests", help=list_requests_usage, description=list_requests_usage
    )
    list_requests_parser.add_argument(
        "-i",
        "--registered-contract-id",
        type=uuid.UUID,
        required=True,
        help="The ID of the registered contract to list call requests for",
    )
    list_requests_parser.add_argument(
        "-c",
        "--caller",
        type=Web3.toChecksumAddress,
        required=True,
        help="Caller's address",
    )
    list_requests_parser.add_argument(
        "-N",
        "--limit",
        type=int,
        required=False,
        default=10,
        help="The number of call requests to return",
    )
    list_requests_parser.add_argument(
        "-n",
        "--offset",
        type=int,
        required=False,
        default=0,
        help="The offset to start returning contracts from",
    )
    list_requests_parser.add_argument(
        "--show-expired",
        action="store_true",
        help="Set this flag to also show expired requests. Default behavior is to hide these.",
    )
    list_requests_parser.set_defaults(func=handle_list_requests)

    return parser


def main() -> None:
    parser = generate_cli()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
