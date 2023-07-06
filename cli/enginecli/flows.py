import argparse
from enum import Enum
import json
import os
import sys
import time
from typing import Any, Dict, Optional, List, Set

from enginecli.core import lootbox_item_to_tuple

from .MockErc20 import MockErc20
from brownie import network

from . import (
    abi,
    Lootbox,
    ITerminus,
)

MAX_UINT = 2**256 - 1

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def handle_create_equippable_pools_from_config(args: argparse.Namespace) -> None:
    with open(args.config_file, "r") as f:
        config = json.load(f)

    if type(config) is not list:
        raise Exception("Config must be a list of equippable items.")

    network.connect(args.network)
    transaction_config = ITerminus.get_transaction_config(args)

    equipment = ITerminus.ITerminus(args.equipment_address)
    print("Started with " + str(equipment.total_pools()) + " pools.")

    for item in config:
        print(item["id"])
        # equipment.create_pool_v2(2**256-1, True, True, item["metadata"], transaction_config)
        # pool_id = equipment.total_pools()

    print("Ended with " + str(equipment.total_pools()) + " pools.")


def handle_create_equippables_lootbox_from_config(args: argparse.Namespace) -> None:
    with open(args.config_file, "r") as f:
        config = json.load(f)

    if type(config) is not list:
        raise Exception("Config must be a list of equippable items.")

    network.connect(args.network)
    transaction_config = ITerminus.get_transaction_config(args)

    lootbox_contract = Lootbox.Lootbox(args.lootbox_address)
    token_address = args.equipment_address

    lootbox_items = []
    for item in config:
        lootbox_items.append(
            lootbox_item_to_tuple(
                reward_type=1155,
                token_address=token_address,
                # TODO: How do I get the pool id for each item?
                token_id=0,
                token_amount=1,
                weight=int(item["weight"] * 1000),
            )
        )

    print(lootbox_items)

    # Magic number "1" is the random lootbox type. Currently it's only enumerated in test file.
    # lootbox_contract.create_lootbox(lootbox_items, 1, transaction_config)


def generate_cli():
    parser = argparse.ArgumentParser(
        description="CLI to manage Lootbox contract",
    )

    parser.set_defaults(func=lambda _: parser.print_help())
    subcommands = parser.add_subparsers()

    create_pools_from_config_parser = subcommands.add_parser(
        "create-pools-from-config",
        help="Creates metagame equipment",
        description="Creates base metagame equipment for Crypto Guilds",
    )

    create_pools_from_config_parser.add_argument(
        "--equipment-address",
        type=str,
        required=True,
        help="Address of the equipment terminus contract",
    )

    create_pools_from_config_parser.add_argument(
        "--config-file",
        type=str,
        required=True,
        help="Path to the config file",
    )

    ITerminus.add_default_arguments(create_pools_from_config_parser, transact=True)

    create_pools_from_config_parser.set_defaults(
        func=handle_create_equippable_pools_from_config
    )

    create_lootbox_from_config_parser = subcommands.add_parser(
        "create-lootbox-from-config",
        help="Creates lootbox",
        description="Creates lootbox with weights from item config file.",
    )

    create_lootbox_from_config_parser.add_argument(
        "--lootbox-address",
        type=str,
        required=True,
        help="Address of the lootbox contract",
    )

    create_lootbox_from_config_parser.add_argument(
        "--equipment-address",
        type=str,
        required=True,
        help="Address of the equipment terminus contract",
    )

    create_lootbox_from_config_parser.add_argument(
        "--config-file",
        type=str,
        required=True,
        help="Path to the config file",
    )

    ITerminus.add_default_arguments(create_lootbox_from_config_parser, transact=True)

    create_lootbox_from_config_parser.set_defaults(
        func=handle_create_equippables_lootbox_from_config
    )

    return parser
