"""
Login functionality for Moonstream Engine.

Login flow relies on an Authorization header passed to Moonstream Engine of the form:
Authorization: moonstream <base64-encoded JSON>

The schema for the JSON object will be as follows:
{
    "address": "<address of account which signed the message>",
    "deadline": <epoch timestamp after which this header becomes invalid>,
    "signature": "<signed authorization message>"
}

Authorization messages will be generated pursuant to EIP712 using the following parameters:
Domain separator - name: MoonstreamAuthorization, version: <Engine API version>
Fields - address ("address" type), deadline: ("uint256" type)
"""
import argparse
import base64
import json
import time
from typing import Any, cast, Dict, Optional

from brownie import accounts
from eip712.messages import EIP712Message
from web3 import Web3

from .version import VERSION

AUTH_PAYLOAD_NAME = "MoonstreamAuthorization"

# By default, authorizations will remain active for 24 hours.
DEFAULT_INTERVAL = 60 * 60 * 24


class MoonstreamAuthorizationVerificationError(Exception):
    pass


class MoonstreamAuthorizationExpired(Exception):
    pass


class MoonstreamAuthorization(EIP712Message):
    _name_: "string"
    _version_: "string"

    address: "address"
    deadline: "uint256"


def authorize(
    deadline: int, account: str, password: Optional[str] = None
) -> Dict[str, Any]:
    signer = accounts.load(account, password)
    message = MoonstreamAuthorization(
        _name_=AUTH_PAYLOAD_NAME,
        _version_=VERSION,
        address=signer.address,
        deadline=deadline,
    )
    signed_message = signer.sign_message(message)

    api_payload: Dict[str, Any] = {
        "address": signer.address,
        "deadline": deadline,
        "signed_message": signed_message.signature.hex(),
    }

    return api_payload


def verify(authorization_payload: Dict[str, Any]) -> bool:
    time_now = int(time.time())
    web3_client = Web3()
    address = cast(str, authorization_payload["address"])
    deadline = cast(int, authorization_payload["deadline"])
    signature = cast(str, authorization_payload["signed_message"])

    message = MoonstreamAuthorization(
        _name_=AUTH_PAYLOAD_NAME,
        _version_=VERSION,
        address=address,
        deadline=deadline,
    )

    signer_address = web3_client.eth.account.recover_message(
        message.signable_message, signature=signature
    )
    if signer_address != address:
        raise MoonstreamAuthorizationVerificationError("Invalid signer")

    if deadline < time_now:
        raise MoonstreamAuthorizationExpired("Deadline exceeded")

    return True


def handle_authorize(args: argparse.Namespace) -> None:
    authorization = authorize(args.deadline, args.signer, args.password)
    print(json.dumps(authorization))


def handle_verify(args: argparse.Namespace) -> None:
    payload_json = base64.decodebytes(args.payload).decode("utf-8")
    payload = json.loads(payload_json)
    verify(payload)
    print("Verified!")


def generate_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Moonstream Engine authorization module"
    )
    subcommands = parser.add_subparsers()

    authorize_parser = subcommands.add_parser("authorize")
    authorize_parser.add_argument(
        "-t",
        "--deadline",
        type=int,
        default=int(time.time()) + DEFAULT_INTERVAL,
        help="Authorization deadline (seconds since epoch timestamp).",
    )
    authorize_parser.add_argument(
        "-s",
        "--signer",
        required=True,
        help="Path to signer keyfile (or brownie account name).",
    )
    authorize_parser.add_argument(
        "-p",
        "--password",
        required=False,
        help="(Optional) password for signing account. If you don't provide it here, you will be prompte for it.",
    )
    authorize_parser.set_defaults(func=handle_authorize)

    verify_parser = subcommands.add_parser("verify")
    verify_parser.add_argument(
        "--payload",
        type=lambda s: s.encode(),
        required=True,
        help="Base64-encoded payload to verify",
    )
    verify_parser.set_defaults(func=handle_verify)

    return parser
