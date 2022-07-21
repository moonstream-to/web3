import argparse
from ast import arg
import json
import os
import sys
import time
from typing import Any, Dict, Optional, List, Set

from engineapi.MockErc20 import MockErc20
from brownie import network


from . import (
    abi,
    Lootbox,
    MockTerminus,
    CraftingFacet,
    Diamond,
    DiamondCutFacet,
    DiamondLoupeFacet,
    OwnershipFacet,
    ReentrancyExploitable,
    CraftingFacet,
)

FACETS: Dict[str, Any] = {
    "DiamondCutFacet": DiamondCutFacet,
    "DiamondLoupeFacet": DiamondLoupeFacet,
    "OwnershipFacet": OwnershipFacet,
    "ReentrancyExploitable": ReentrancyExploitable,
    "CraftingFacet": CraftingFacet,
}

FACET_PRECEDENCE: List[str] = [
    "DiamondCutFacet",
    "OwnershipFacet",
    "DiamondLoupeFacet",
]

FACET_ACTIONS: Dict[str, int] = {"add": 0, "replace": 1, "remove": 2}

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def facet_cut(
    diamond_address: str,
    facet_name: str,
    facet_address: str,
    action: str,
    transaction_config: Dict[str, Any],
    initializer_address: str = ZERO_ADDRESS,
    ignore_methods: Optional[List[str]] = None,
    ignore_selectors: Optional[List[str]] = None,
    methods: Optional[List[str]] = None,
    selectors: Optional[List[str]] = None,
) -> Any:
    """
    Cuts the given facet onto the given Diamond contract.

    Resolves selectors in the precedence order defined by FACET_PRECEDENCE (highest precedence first).
    """
    assert (
        facet_name in FACETS
    ), f"Invalid facet: {facet_name}. Choices: {','.join(FACETS)}."

    assert (
        action in FACET_ACTIONS
    ), f"Invalid cut action: {action}. Choices: {','.join(FACET_ACTIONS)}."

    if ignore_methods is None:
        ignore_methods = []
    if ignore_selectors is None:
        ignore_selectors = []
    if methods is None:
        methods = []
    if selectors is None:
        selectors = []

    project_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    abis = abi.project_abis(project_dir)

    reserved_selectors: Set[str] = set()
    for facet in FACET_PRECEDENCE:
        if facet == facet_name:
            break

        facet_abi = abis.get(facet, [])
        for item in facet_abi:
            if item["type"] == "function":
                reserved_selectors.add(abi.encode_function_signature(item))

    facet_function_selectors: List[str] = []
    facet_abi = abis.get(facet_name, [])

    logical_operator = all
    method_predicate = lambda method: method not in ignore_methods
    selector_predicate = (
        lambda selector: selector not in reserved_selectors
        and selector not in ignore_selectors
    )

    if len(methods) > 0 or len(selectors) > 0:
        logical_operator = any
        method_predicate = lambda method: method in methods
        selector_predicate = lambda selector: selector in selectors

    for item in facet_abi:
        if item["type"] == "function":
            item_selector = abi.encode_function_signature(item)
            if logical_operator(
                [method_predicate(item["name"]), selector_predicate(item_selector)]
            ):
                facet_function_selectors.append(item_selector)

    target_address = facet_address
    if FACET_ACTIONS[action] == 2:
        target_address = ZERO_ADDRESS

    diamond_cut_action = [
        target_address,
        FACET_ACTIONS[action],
        facet_function_selectors,
    ]

    diamond = DiamondCutFacet.DiamondCutFacet(diamond_address)
    calldata = b""
    transaction = diamond.diamond_cut(
        [diamond_cut_action], initializer_address, calldata, transaction_config
    )
    return transaction


def crafting_gogogo(
    owner_address: str, transaction_config: Dict[str, Any]
) -> Dict[str, Any]:
    result = diamond_gogogo(owner_address, transaction_config)

    try:
        crafting_facet = CraftingFacet.CraftingFacet(None)
        crafting_facet.deploy(transaction_config)
    except Exception as e:
        print(e)
        result["error"] = f"Failed to deploy CraftingFacet: {e}"
        return result

    result["CraftingFacet"] = crafting_facet.address

    try:
        facet_cut(
            result["Diamond"],
            "CraftingFacet",
            crafting_facet.address,
            "add",
            transaction_config,
        )
    except Exception as e:
        print(e)
        result["error"] = f"Failed to diamondCut cut CraftingFacet: {e}"
        return result

    result["attached"].append("CraftingFacet")
    return result


def diamond_gogogo(
    owner_address: str, transaction_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Deploy diamond along with all its basic facets and attach those facets to the diamond.

    Returns addresses of all the deployed contracts with the contract names as keys.
    """
    result: Dict[str, Any] = {}

    try:
        diamond_cut_facet = DiamondCutFacet.DiamondCutFacet(None)
        diamond_cut_facet.deploy(transaction_config)
    except Exception as e:
        print(e)
        result["error"] = "Failed to deploy DiamondCutFacet"
        return result
    result["DiamondCutFacet"] = diamond_cut_facet.address

    try:
        diamond = Diamond.Diamond(None)
        diamond.deploy(owner_address, diamond_cut_facet.address, transaction_config)
    except Exception as e:
        print(e)
        result["error"] = "Failed to deploy Diamond"
        return result
    result["Diamond"] = diamond.address

    try:
        diamond_loupe_facet = DiamondLoupeFacet.DiamondLoupeFacet(None)
        diamond_loupe_facet.deploy(transaction_config)
    except Exception as e:
        print(e)
        result["error"] = "Failed to deploy DiamondLoupeFacet"
        return result
    result["DiamondLoupeFacet"] = diamond_loupe_facet.address

    try:
        ownership_facet = OwnershipFacet.OwnershipFacet(None)
        ownership_facet.deploy(transaction_config)
    except Exception as e:
        print(e)
        result["error"] = "Failed to deploy OwnershipFacet"
        return result
    result["OwnershipFacet"] = ownership_facet.address

    result["attached"] = []

    try:
        facet_cut(
            diamond.address,
            "DiamondLoupeFacet",
            diamond_loupe_facet.address,
            "add",
            transaction_config,
        )
    except Exception as e:
        print(e)
        result["error"] = "Failed to attach DiamondLoupeFacet"
        return result
    result["attached"].append("DiamondLoupeFacet")

    try:
        facet_cut(
            diamond.address,
            "OwnershipFacet",
            ownership_facet.address,
            "add",
            transaction_config,
        )
    except Exception as e:
        print(e)
        result["error"] = "Failed to attach OwnershipFacet"
        return result
    result["attached"].append("OwnershipFacet")

    return result


def lootbox_item_to_tuple(
    reward_type: int,
    token_address: str,
    token_id: int,
    token_amount: int,
    weight: int = 0,
):
    return (reward_type, token_address, token_id, token_amount, weight)


def lootbox_item_tuple_to_json_file(tuple_item, file_path: str):
    item = {
        "rewardType": tuple_item[0],
        "tokenAddress": tuple_item[1],
        "tokenId": tuple_item[2],
        "tokenAmount": tuple_item[3],
        "weight": tuple_item[4],
    }
    with open(file_path, "w") as f:
        json.dump(item, f)


def _lootbox_item_from_json_object(item: Dict[str, Any]) -> Any:
    return lootbox_item_to_tuple(
        item["rewardType"],
        item["tokenAddress"],
        item["tokenId"],
        item["tokenAmount"],
        item["weight"],
    )


def load_lootbox_items_from_json_file(file_path: str):
    with open(file_path, "r") as f:
        items = json.load(f)
    return [_lootbox_item_from_json_object(item) for item in items]


def load_lootbox_item_from_json_file(file_path: str):
    with open(file_path, "r") as f:
        item = json.load(f)
    return lootbox_item_to_tuple(
        item["rewardType"],
        item["tokenAddress"],
        item["tokenId"],
        item["tokenAmount"],
    )


def create_lootboxes_from_config(
    lootbox_address: str, filepath: str, tx_config, yes: Optional[bool] = False
) -> Dict[str, Any]:
    with open(filepath, "r") as f:
        config = json.load(f)

    if type(config) is not list:
        raise Exception("Config must be a list of lootboxes")

    lootboxes = []
    lootbox_contract = Lootbox.Lootbox(lootbox_address)
    terminus_address = lootbox_contract.terminus_address()

    terminus = MockTerminus.MockTerminus(terminus_address)

    pool_creation_fee = terminus.pool_base_price()
    contract_payment_balance = MockErc20(terminus.payment_token()).balance_of(
        lootbox_address
    )

    if contract_payment_balance < pool_creation_fee * len(config):
        raise Exception(
            f"Lootbox contract does not have enough tokens to create terminus pool."
            f"Need {pool_creation_fee * len(config)} but only have {contract_payment_balance}"
        )

    for lootbox in config:  # This is for validating data

        lootbox_items = []
        for item in lootbox["items"]:
            if item["rewardType"] == 20:
                erc20_contract = MockErc20(item["tokenAddress"])
                erc20_decimals = erc20_contract.decimals()
                item["tokenAmount"] *= 10 ** erc20_decimals
            lootbox_items.append(_lootbox_item_from_json_object(item))

        lootboxes.append(
            {
                "name": lootbox["name"],
                "lootboxType": lootbox["lootboxType"],
                "tokenUri": lootbox.get("tokenUri"),
                "items": lootbox_items,
            }
        )

    print(f"Giving Terminus control to Lootbox contract: {lootbox_contract.address}")
    terminus.set_controller(lootbox_contract.address, tx_config)

    try:
        current_lootbox_id = lootbox_contract.total_lootbox_count() - 1
        print(
            f"There are already {current_lootbox_id + 1} lootboxes created on this contract."
        )

        results = []
        for lootbox in lootboxes:
            print(f"Creating lootbox {lootbox['name']}...")
            print(f"Items: {lootbox['items']}")

            lootbox_contract.create_lootbox(
                lootbox["items"],
                lootbox["lootboxType"],
                tx_config,
            )

            current_lootbox_id += 1
            lootbox_id = lootbox_contract.total_lootbox_count() - 1

            while True:
                if yes:
                    break
                lootbox_id = lootbox_contract.total_lootbox_count() - 1
                is_ok = input(
                    f"lootboxId is {lootbox_id}. Should be {current_lootbox_id} Continue? (y/n)"
                )
                if is_ok == "y":
                    break
                elif is_ok == "n":
                    print("Waiting 30 secs...")
                    time.sleep(30)
                    continue
                else:
                    print("Invalid input")
                    continue

            terminus_pool_id = lootbox_contract.terminus_pool_idby_lootbox_id(
                lootbox_id
            )
            results.append(
                {
                    "name": lootbox["name"],
                    "tokenUri": lootbox["tokenUri"],
                    "lootboxId": lootbox_id,
                    "lootboxType": lootbox["lootboxType"],
                    "items": lootbox["items"],
                    "terminusPoolId": terminus_pool_id,
                }
            )

            if lootbox.get("tokenUri") is not None:
                print(f"Setting lootbox {lootbox['name']} lootbox URI...")
                lootbox_contract.set_lootbox_uri(
                    lootbox_id, lootbox["tokenUri"], tx_config
                )
                print("\n")
    finally:
        print(
            f"Surrendering Terminus control back to caller: {tx_config['from'].address}"
        )
        lootbox_contract.surrender_terminus_control(tx_config)

    return results


def gogogo(
    terminus_address,
    vrf_coordinator_address,
    link_token_address,
    chainlik_vrf_fee,
    chainlik_vrf_keyhash,
    tx_config,
) -> Dict[str, Any]:
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
    lootbox_contract.deploy(
        terminus_address,
        admin_token_pool_id,
        vrf_coordinator_address,
        link_token_address,
        chainlik_vrf_fee,
        chainlik_vrf_keyhash,
        tx_config,
    )

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
    result = gogogo(
        terminus_address,
        args.vrf_coordinator_address,
        args.link_token_address,
        args.chainlik_vrf_fee,
        args.chainlik_vrf_keyhash,
        transaction_config,
    )

    if args.outfile is not None:
        with args.outfile:
            json.dump(result, args.outfile)
    json.dump(result, sys.stdout, indent=4)


def handle_crafting_gogogo(args: argparse.Namespace) -> None:
    network.connect(args.network)

    transaction_config = MockTerminus.get_transaction_config(args)
    result = crafting_gogogo(
        args.owner_address,
        transaction_config,
    )

    if args.outfile is not None:
        with args.outfile:
            json.dump(result, args.outfile)
    json.dump(result, sys.stdout, indent=4)


def handle_create_lootboxes_from_config(args: argparse.Namespace) -> None:
    network.connect(args.network)
    transaction_config = MockTerminus.get_transaction_config(args)

    result = create_lootboxes_from_config(
        args.address, args.config_file, transaction_config, args.yes
    )
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

    gogogo_parser.add_argument(
        "--vrf-coordinator-address",
        type=str,
        required=True,
        help="Address of the vrf coordinator contract",
    )

    gogogo_parser.add_argument(
        "--link-token-address",
        type=str,
        required=True,
        help="Address of the link token contract",
    )

    gogogo_parser.add_argument(
        "--chainlik-vrf-fee",
        type=int,
        required=True,
        help="Chainlink vrf fee",
    )

    gogogo_parser.add_argument(
        "--chainlik-vrf-keyhash",
        type=str,
        required=True,
        help="Chainlink vrf keyhash",
    )

    MockTerminus.add_default_arguments(gogogo_parser, transact=True)

    gogogo_parser.set_defaults(func=handle_gogogo)

    crafting_gogogo_parser = subcommands.add_parser(
        "crafting-gogogo",
        help="Deploys Crafting contract",
        description="Deploys Crafting contract",
    )

    crafting_gogogo_parser.add_argument(
        "-o",
        "--outfile",
        type=argparse.FileType("w"),
        default=None,
        help="(Optional) file to write deployed addresses to",
    )

    crafting_gogogo_parser.add_argument(
        "--owner-address",
        type=str,
        required=True,
        help="Address of the owner of the lootbox contract",
    )

    MockTerminus.add_default_arguments(crafting_gogogo_parser, transact=True)

    crafting_gogogo_parser.set_defaults(func=handle_crafting_gogogo)

    create_lootboxes_from_config_parser = subcommands.add_parser(
        "create-lootboxes-from-config",
        help="Creates lootboxes from config",
        description="Creates lootboxes from config",
    )

    create_lootboxes_from_config_parser.add_argument(
        "-o",
        "--outfile",
        type=argparse.FileType("w"),
        default=None,
        help="(Optional) file to write deployed addresses to",
    )

    create_lootboxes_from_config_parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Not verify lootboxId",
    )

    create_lootboxes_from_config_parser.add_argument(
        "--config-file",
        type=str,
        required=True,
        help="Path to the config file",
    )

    MockTerminus.add_default_arguments(
        create_lootboxes_from_config_parser, transact=True
    )

    create_lootboxes_from_config_parser.set_defaults(
        func=handle_create_lootboxes_from_config
    )

    return parser
