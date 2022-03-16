import argparse
from ast import arg
import json
import sys
from typing import Any, Dict

from lootbox.MockErc20 import MockErc20
from brownie import network
from . import Lootbox, MockTerminus


def lootbox_item_to_tuple(
    reward_type: int, token_address: str, token_id: int, token_amount: int
):
    return (reward_type, token_address, token_id, token_amount)


def lootbox_item_tuple_to_json_file(tuple_item, file_path: str):
    item = {
        "rewardType": tuple_item[0],
        "tokenAddress": tuple_item[1],
        "tokenId": tuple_item[2],
        "tokenAmount": tuple_item[3],
    }
    with open(file_path, "w") as f:
        json.dump(item, f)


def load_lootbox_item_from_json_file(file_path: str):
    with open(file_path, "r") as f:
        item = json.load(f)
    return lootbox_item_to_tuple(
        item["rewardType"], item["tokenAddress"], item["tokenId"], item["tokenAmount"]
    )


def gogogo(terminus_address, tx_config) -> Dict[str, Any]:

    deployer = tx_config["from"]
    terminus_contract = MockTerminus.MockTerminus(terminus_address)

    terminus_payment_token_address = terminus_contract.payment_token()
    terminus_payment_token = MockErc20(terminus_payment_token_address)

    pool_base_price = terminus_contract.pool_base_price()
    deployer_payment_token_balance = terminus_payment_token.balance_of(deployer.address)

    if deployer_payment_token_balance < pool_base_price:
        raise Exception(
            f"Deployer does not have enough tokens to create terminus pool."
            f"Need {pool_base_price} but only have {deployer_payment_token_balance}"
        )

    print("Approving deployer to spend tokens to create terminus pool...")
    terminus_payment_token.approve(terminus_address, pool_base_price, tx_config)

    print("Creating terminus pool...")
    terminus_contract.create_pool_v1(pool_base_price, False, True, tx_config)

    admin_token_pool_id = terminus_contract.total_pools()

    print("Deploying lootbox...")
    lootbox_contract = Lootbox.Lootbox(None)
    lootbox_contract.deploy(terminus_address, admin_token_pool_id, tx_config)

    print("Setting pool controller...")
    terminus_contract.set_pool_controller(
        admin_token_pool_id, lootbox_contract.address, tx_config
    )

    contracts = {
        "Lootbox": lootbox_contract.address,
        "adminTokenPoolId": admin_token_pool_id,
    }

    return contracts


def handle_gogogo(args: argparse.Namespace) -> None:
    network.connect(args.network)
    terminus_address = args.terminus_address
    transaction_config = MockTerminus.get_transaction_config(args)
    result = gogogo(terminus_address, transaction_config)
    if args.outfile is not None:
        with args.outfile:
            json.dump(result, args.outfile)
    json.dump(result, sys.stdout, indent=4)


def generate_cli():
    parser = argparse.ArgumentParser(
        description="CLI to manage Lootbox contract",
    )

    parser.set_defaults(func=lambda _: parser.print_help())
    subcommands = parser.add_subparsers()

    gogogo_parser = subcommands.add_parser(
        "gogogo",
        help="Deploys Lootbox contract",
        description="Deploys Lootbox contract",
    )

    gogogo_parser.add_argument(
        "-o",
        "--outfile",
        type=argparse.FileType("w"),
        default=None,
        help="(Optional) file to write deployed addresses to",
    )

    gogogo_parser.add_argument(
        "--terminus-address",
        type=str,
        required=True,
        help="Address of the terminus contract",
    )

    MockTerminus.add_default_arguments(gogogo_parser, transact=True)

    gogogo_parser.set_defaults(func=handle_gogogo)

    return parser
