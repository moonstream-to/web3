import argparse
from enum import Enum
import json
import csv
import os
from re import I
import sys
from textwrap import indent
import time
from typing import Any, Dict, Optional, List, Set

from enginecli.core import lootbox_item_to_tuple

from .MockErc20 import MockErc20
from brownie import network

from . import abi, Lootbox, ITerminus, InventoryFacet

MAX_UINT = 2**256 - 1

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def handle_create_item_pools_from_config(args: argparse.Namespace) -> None:
    with open(args.config_file, "r") as f:
        config = json.load(f)

    if type(config) is not list:
        raise Exception("Config must be a list of equippable items.")

    network.connect(args.network)
    transaction_config = ITerminus.get_transaction_config(args)

    equipment = ITerminus.ITerminus(args.equipment_address)
    print("Started with " + str(equipment.total_pools()) + " pools.")

    print("{Item Id} => {Pool Id}")
    for item in config:
        equipment.create_pool_v2(
            MAX_UINT, True, True, item["metadata"], transaction_config
        )
        pool_id = equipment.total_pools()
        print(item["id"] + " => " + str(pool_id))

    print("Ended with " + str(equipment.total_pools()) + " pools.")


def handle_create_items_lootbox_from_config(args: argparse.Namespace) -> None:
    with open(args.config_file, "r") as f:
        config = json.load(f)

    if type(config) is not list:
        raise Exception("Config must be a list of equippable items.")

    print(args.lootbox_pool_id)

    network.connect(args.network)
    transaction_config = ITerminus.get_transaction_config(args)

    lootbox_contract = Lootbox.Lootbox(args.lootbox_address)
    equipment = ITerminus.ITerminus(args.equipment_address)

    lootbox_items = []
    for item in config:
        lootbox_items.append(
            lootbox_item_to_tuple(
                reward_type=1,
                token_address=args.equipment_address,
                token_id=item["pool_id"],
                token_amount=1,
                weight=int(item["weight"] * 1000),
            )
        )
        equipment.approve_for_pool(
            item["pool_id"], args.lootbox_address, transaction_config
        )

    print(lootbox_items)

    # Magic number "1" is the random lootbox type. Currently it's only enumerated in test file.
    lootbox_contract.create_lootbox_with_terminus_pool(
        lootbox_items, args.lootbox_pool_id, 1, transaction_config
    )


def handle_create_inventory_slots_from_config(args: argparse.Namespace) -> None:
    with open(args.config_file, "r") as f:
        config = json.load(f)

    if type(config) is not list:
        raise Exception("Config must be a list of equippable items.")

    network.connect(args.network)
    transaction_config = ITerminus.get_transaction_config(args)

    inventory = InventoryFacet.InventoryFacet(args.inventory_address)
    equipment_address = args.equipment_address

    slot_type_mapping = dict()
    slot_mapping = dict()
    pool_mapping = dict()

    # No good way to search the existing slot types. This just starts creating slot types from id 11. Perhaps it could be a parameter, but really
    # needs a contract change to support slot type creation.
    next_slot_type_id = 11
    for item in config:
        slot_type = item["type"]
        if not slot_type in slot_type_mapping:
            inventory.create_slot_type(next_slot_type_id, slot_type, transaction_config)
            slot_type_mapping[slot_type] = next_slot_type_id
            print(
                "Created slot type " + slot_type + " with id " + str(next_slot_type_id)
            )
            inventory.create_slot(True, next_slot_type_id, "", transaction_config)
            next_slot_id = inventory.num_slots()
            slot_mapping[slot_type] = next_slot_id
            print(
                "Created slot with type " + slot_type + " and id " + str(next_slot_id)
            )
            next_slot_type_id = next_slot_type_id + 1
        pool_id = item["pool_id"]
        slot_id = slot_mapping[slot_type]
        inventory.mark_item_as_equippable_in_slot(
            slot_id,
            1155,
            equipment_address,
            pool_id,
            1,
            transaction_config,
        )
        pool_mapping[item["id"]] = {
            "pool_id": pool_id,
            "slot_id": slot_id,
            "slot_type": slot_type,
        }
        print(item["id"] + " is equippable in slot " + str(slot_id))

    print(slot_type_mapping)
    print(slot_mapping)
    print(pool_mapping)


def handle_create_metadata_from_csv(args: argparse.Namespace) -> None:
    dir = os.path.dirname(args.csv_file)

    with open(args.csv_file, "r") as f:
        reader = csv.DictReader(f)
        i = 0
        config = []
        for row in reader:
            i = i + 1
            item_voucher_id = row["Voucher ID"]
            item_name = row["Name"]
            item_class = row["Class"]
            item_rarity = row["Rarity"]
            item_image = row["Image Type"].lower()
            item_shadowcorn_id = row["Shadowcorn/Egg ID"]
            base_descripton = "Standing proud in all of its terrifying glory, behold the Shadowcorn Figurine! Legends speak of how this mighty idol sprang forth from a dark and enigmatic Shadowcorn Egg that was crafted deep in the bustling crafting halls of IsmToys, where the master figurine-smiths practice the ancient techniques needed to adequately capture the menacing essence of  a Shadowcorn’s visage! Redeem this voucher via the https://unicorns-beryl.vercel.app/ and receive your very own Shadowcorn Figurine!"
            related_shadowcorn_url = (
                "https://www.hawku.com/details/crypto-unicorns/shadowcorn/{}".format(
                    item_shadowcorn_id
                )
            )
            description = (
                base_descripton
                + " This voucher will claim a Shadowcorn Figurine that mirrors the appearance and name of Shadowcorn [{}]({})."
            ).format(item_shadowcorn_id, related_shadowcorn_url)
            if item_name != "":
                config.append(
                    {
                        "id": item_voucher_id,
                        "metadata": "https://badges.moonstream.to/cu-vouchers/voucher-{}.json".format(
                            item_voucher_id
                        ),
                    }
                )
                metadata = {
                    "name": item_name + " Voucher",
                    "description": description,
                    "image": "https://badges.moonstream.to/cu-vouchers/images/{}.png".format(
                        item_image
                    ),
                    "external_url": "https://www.cryptounicorns.fun/",
                    "metadata_version": 1,
                    "attributes": [
                        {"trait_type": "token_type", "value": "voucher"},
                        {"trait_type": "rarity", "value": item_rarity},
                        {"trait_type": "class", "value": item_class},
                        # {
                        #     "trait_type": "related_shadowcorn_url",
                        #     "value": "https://opensea.io/assets/matic/0xa7d50ee3d7485288107664cf758e877a0d351725/{}".format(
                        #         item_shadowcorn_id
                        #     ),
                        # },
                        {"trait_type": "protocol", "value": "terminus"},
                    ],
                }

                outfile = os.path.join(
                    dir, "metadata", "voucher-{}.json".format(item_voucher_id)
                )
                if outfile is not None:
                    with open(outfile, "w") as o:
                        json.dump(metadata, o, indent=4)
        if len(config) > 0:
            config_file = os.path.join(dir, "config.json")
            if config_file is not None:
                with open(config_file, "w") as conf:
                    json.dump(config, conf, indent=4)


def generate_cli():
    parser = argparse.ArgumentParser(
        description="CLI to manage Lootbox contract",
    )

    parser.set_defaults(func=lambda _: parser.print_help())
    subcommands = parser.add_subparsers()

    create_item_pools_from_config_parser = subcommands.add_parser(
        "create-item-pools-from-config",
        help="Creates metagame equipment",
        description="Creates base metagame equipment for Crypto Guilds",
    )

    create_item_pools_from_config_parser.add_argument(
        "--equipment-address",
        type=str,
        required=True,
        help="Address of the equipment terminus contract",
    )

    create_item_pools_from_config_parser.add_argument(
        "--config-file",
        type=str,
        required=True,
        help="Path to the config file",
    )

    ITerminus.add_default_arguments(create_item_pools_from_config_parser, transact=True)

    create_item_pools_from_config_parser.set_defaults(
        func=handle_create_item_pools_from_config
    )

    create_items_lootbox_from_config_parser = subcommands.add_parser(
        "create-items-lootbox-from-config",
        help="Creates lootbox",
        description="Creates lootbox with weights from item config file.",
    )

    create_items_lootbox_from_config_parser.add_argument(
        "--lootbox-address",
        type=str,
        required=True,
        help="Address of the lootbox contract",
    )

    create_items_lootbox_from_config_parser.add_argument(
        "--equipment-address",
        type=str,
        required=True,
        help="Address of the equipment terminus contract",
    )

    create_items_lootbox_from_config_parser.add_argument(
        "--lootbox-pool-id",
        type=str,
        required=True,
        help="Terminus pool housing lootboxes created by the contract",
    )

    create_items_lootbox_from_config_parser.add_argument(
        "--config-file",
        type=str,
        required=True,
        help="Path to the config file",
    )

    ITerminus.add_default_arguments(
        create_items_lootbox_from_config_parser, transact=True
    )

    create_items_lootbox_from_config_parser.set_defaults(
        func=handle_create_items_lootbox_from_config
    )

    create_inventory_slots_from_config_parser = subcommands.add_parser(
        "create-inventory-slots-from-config",
        help="Creates Inventory slots",
        description="Creates inventory slots with types from config file.",
    )

    create_inventory_slots_from_config_parser.add_argument(
        "--inventory-address",
        type=str,
        required=True,
        help="Address of the lootbox contract",
    )

    create_inventory_slots_from_config_parser.add_argument(
        "--equipment-address",
        type=str,
        required=True,
        help="Address of the equipment (terminus) contract",
    )

    create_inventory_slots_from_config_parser.add_argument(
        "--config-file",
        type=str,
        required=True,
        help="Path to the config file",
    )

    ITerminus.add_default_arguments(
        create_inventory_slots_from_config_parser, transact=True
    )

    create_inventory_slots_from_config_parser.set_defaults(
        func=handle_create_inventory_slots_from_config
    )

    create_metadata_from_csv = subcommands.add_parser(
        "create-metadata-from-csv",
        help="Creates config file",
        description="Creates config file with.",
    )

    create_metadata_from_csv.set_defaults(func=handle_create_metadata_from_csv)

    create_metadata_from_csv.add_argument(
        "--csv-file",
        type=str,
        required=True,
        help="Path to the csv file",
    )

    return parser
