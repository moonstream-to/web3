import argparse
from enum import Enum
import json
import os
import sys
import time
from typing import Any, Dict, Optional, List, Set

from .MockErc20 import MockErc20
from brownie import network

from . import (
    abi,
    Lootbox,
    ITerminus,
)

MAX_UINT = 2**256 - 1

METAGAME_EQUIPMENT: List[object] = [
    {
        "id": "primal_armor_common",
        "type": "armor",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/armor/primal-armor-common.json",
    },
    {
        "id": "primal_armor_rare",
        "type": "armor",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/armor/primal-armor-rare.json",
    },
    {
        "id": "primal_armor_epic",
        "type": "armor",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/armor/primal-armor-epic.json",
    },
    {
        "id": "primal_armor_legendary",
        "type": "armor",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/armor/primal-armor-legendary.json",
    },
    {
        "id": "brawlers_boots_common",
        "type": "boots",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/boots/brawlers-boots-common.json",
    },
    {
        "id": "brawlers_boots_rare",
        "type": "boots",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/boots/brawlers-boots-rare.json",
    },
    {
        "id": "brawlers_boots_epic",
        "type": "boots",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/boots/brawlers-boots-epic.json",
    },
    {
        "id": "brawlers_boots_legendary",
        "type": "boots",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/boots/brawlers-boots-legendary.json",
    },
    {
        "id": "charged_bracers_common",
        "type": "bracers",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/bracers/charged-bracers-common.json",
    },
    {
        "id": "charged_bracers_rare",
        "type": "bracers",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/bracers/charged-bracers-rare.json",
    },
    {
        "id": "charged_bracers_epic",
        "type": "bracers",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/bracers/charged-bracers-epic.json",
    },
    {
        "id": "charged_bracers_legendary",
        "type": "bracers",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/bracers/charged-bracers-legendary.json",
    },
    {
        "id": "skull_mask_common",
        "type": "helmet",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/helmet/skull-mask-common.json",
    },
    {
        "id": "skull_mask_rare",
        "type": "helmet",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/helmet/skull-mask-rare.json",
    },
    {
        "id": "skull_mask_epic",
        "type": "helmet",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/helmet/skull-mask-epic.json",
    },
    {
        "id": "skull_mask_legendary",
        "type": "helmet",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/helmet/skull-mask-legendary.json",
    },
    {
        "id": "double_axe_common",
        "type": "weapon",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/weapon/double-axe-common.json",
    },
    {
        "id": "double_axe_rare",
        "type": "weapon",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/weapon/double-axe-rare.json",
    },
    {
        "id": "double_axe_epic",
        "type": "weapon",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/weapon/double-axe-epic.json",
    },
    {
        "id": "double_axe_legendary",
        "type": "weapon",
        "metadata": "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/weapon/double-axe-legendary.json ",
    },
]

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def handle_create_metagame_equipment(args: argparse.Namespace) -> None:
    network.connect(args.network)
    transaction_config = ITerminus.get_transaction_config(args)

    equipment = ITerminus.ITerminus(args.equipment_address)
    print("Started with " + str(equipment.total_pools()) + " pools.")

    for item in METAGAME_EQUIPMENT:
        print(item["id"])
        # equipment.create_pool_v2(2**256-1, True, True, item["metadata"], transaction_config)
        # pool_id = equipment.total_pools()

    print("Ended with " + str(equipment.total_pools()) + " pools.")


def generate_cli():
    parser = argparse.ArgumentParser(
        description="CLI to manage Lootbox contract",
    )

    parser.set_defaults(func=lambda _: parser.print_help())
    subcommands = parser.add_subparsers()

    create_metagame_equipment_parser = subcommands.add_parser(
        "create-metagame-equipment",
        help="Creates metagame equipment",
        description="Creates base metagame equipment for Crypto Guilds",
    )

    create_metagame_equipment_parser.add_argument(
        "-o",
        "--outfile",
        type=argparse.FileType("w"),
        default=None,
        help="(Optional) file to write deployed addresses to",
    )

    create_metagame_equipment_parser.add_argument(
        "--equipment-address",
        type=str,
        required=True,
        help="Address of the equipment contract",
    )

    ITerminus.add_default_arguments(create_metagame_equipment_parser, transact=True)

    create_metagame_equipment_parser.set_defaults(func=handle_create_metagame_equipment)

    return parser
