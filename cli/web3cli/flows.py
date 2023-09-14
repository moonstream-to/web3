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

from .core import lootbox_item_to_tuple

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
    next_slot_type_id = 21
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


def handle_create_metadata_from_images(args: argparse.Namespace) -> None:
    dir = args.source_dir
    config = []

    for filename in os.listdir(dir):
        if filename[-4:] != ".png":
            continue

        f = os.path.join(dir, filename)
        # checking if it is a file
        if os.path.isfile(f):
            item_name = get_name_from_filename(filename)
            item_rarity = get_rarity_from_filename(filename)
            item_type = get_type_from_filename(filename)
            item_description = get_description_from_filename(filename)
            item_image_url = build_s3path(filename)
            item_points = get_points_from_filename(filename)

            metadata = {
                "name": item_name,
                "description": item_description,
                "image": item_image_url,
                "external_url": "https://www.crypto-guilds.com/",
                "metadata_version": 1,
                "attributes": [
                    {"trait_type": "token_type", "value": "equipment"},
                    {"trait_type": "rarity", "value": item_rarity},
                    {"trait_type": "slot", "value": item_type},
                    {"trait_type": "points", "value": item_points},
                    {"trait_type": "protocol", "value": "terminus"},
                ],
            }

            if item_rarity != "":
                meta_file = filename.replace("png", "json")

                config.append(
                    {
                        "id": filename[:-4],
                        "type": item_type,
                        "metadata": build_s3path(meta_file),
                        "weight": get_weight_from_rarity(item_rarity),
                        "pool_id": 0,
                    }
                )

                outfile = os.path.join(dir, meta_file)
                if outfile is not None:
                    with open(outfile, "w") as o:
                        json.dump(metadata, o, indent=4)

    if len(config) > 0:
        config_file = os.path.join(dir, "config.json")
        if config_file is not None:
            with open(config_file, "w") as conf:
                json.dump(config, conf, indent=4)


def get_name_from_filename(name: str):
    parts = map(lambda x: x.capitalize(), name.split("-"))
    return " ".join(list(parts)[:-1])


def get_rarity_from_filename(name: str):
    legendary = "legendary"
    epic = "epic"
    rare = "rare"
    common = "common"
    if legendary in name:
        return legendary
    elif epic in name:
        return epic
    elif rare in name:
        return rare
    elif common in name:
        return common
    else:
        return ""


def get_type_from_filename(name: str):
    if "girdle" in name:
        return "belt"
    elif "band" in name:
        return "ring"
    elif "leggings" in name:
        return "leggings"
    elif "cape" in name:
        return "cape"
    elif "shoulders" in name:
        return "shoulders"
    else:
        return ""


def get_description_from_filename(name: str):
    loot_type = get_type_from_filename(name)
    if loot_type == "belt":
        return "Fasten the Warlord's Girdle, a battle-hardened belt imbued with the spirits of ancient warriors, granting you unmatched strength and indomitable will in the heat of combat."
    elif loot_type == "ring":
        return "Wield the Ring of Valor, a band of courage that magnifies your bravery and resilience, turning the tide of battle in your favor with each pulse of its radiant energy."
    elif loot_type == "leggings":
        return "Embrace the enigma of Cursed Leggings, a malevolent garment that grants eerie power at a price as unpredictable as its dark enchantments."
    elif loot_type == "cape":
        return "Unfurl the Vortex Cape, a swirling tapestry of cosmic fabric that not only shields you from harm but also distorts the very air around you, creating miniature whirlwinds in your wake."
    elif loot_type == "shoulders":
        return "Don the Etherguard Shoulders, a set of pauldrons infused with mystical aether, offering both formidable defense and a conduit for channeling ethereal energies."
    else:
        return ""


def build_s3path(filename: str):
    loot_type = get_type_from_filename(filename)
    base = (
        "https://badges.moonstream.to/crypto-guilds/meta-game-launch-items/equipment/"
    )
    return base + loot_type + "/" + filename


def get_points_from_filename(name: str):
    loot_rarity = get_rarity_from_filename(name)
    if loot_rarity == "legendary":
        return 10
    elif loot_rarity == "epic":
        return 5
    elif loot_rarity == "rare":
        return 2
    elif loot_rarity == "common":
        return 1
    else:
        return 0


def get_weight_from_rarity(rarity: str):
    if rarity == "legendary":
        return 0.001
    elif rarity == "epic":
        return 0.009
    elif rarity == "rare":
        return 0.06
    elif rarity == "common":
        return 0.13
    else:
        return 0


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

    create_metadata_from_images = subcommands.add_parser(
        "create-metadata-from-images",
        help="Creates config file",
        description="Creates config file with.",
    )

    create_metadata_from_images.set_defaults(func=handle_create_metadata_from_images)

    create_metadata_from_images.add_argument(
        "--source-dir",
        type=str,
        required=True,
        help="Path to the images",
    )

    return parser
