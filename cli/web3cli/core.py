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
    MockTerminus,
    CraftingFacet,
    Diamond,
    DiamondCutFacet,
    DiamondLoupeFacet,
    DropperFacet,
    OwnershipFacet,
    ReentrancyExploitable,
    CraftingFacet,
    GOFPFacet,
    InventoryFacet,
)

FACETS: Dict[str, Any] = {
    "DiamondCutFacet": DiamondCutFacet,
    "DiamondLoupeFacet": DiamondLoupeFacet,
    "DropperFacet": DropperFacet,
    "OwnershipFacet": OwnershipFacet,
    "ReentrancyExploitable": ReentrancyExploitable,
    "CraftingFacet": CraftingFacet,
    "GOFPFacet": GOFPFacet,
    "InventoryFacet": InventoryFacet,
}

FACET_INIT_CALLDATA: Dict[str, str] = {
    "DropperFacet": lambda address, *args: DropperFacet.DropperFacet(
        address
    ).contract.init.encode_input(*args),
    "GOFPFacet": lambda address, *args: GOFPFacet.GOFPFacet(
        address
    ).contract.init.encode_input(*args),
    "InventoryFacet": lambda address, *args: InventoryFacet.InventoryFacet(
        address
    ).contract.init.encode_input(*args),
}

DIAMOND_FACET_PRECEDENCE: List[str] = [
    "DiamondCutFacet",
    "OwnershipFacet",
    "DiamondLoupeFacet",
]

FACET_PRECEDENCE: List[str] = [
    "DiamondCutFacet",
    "OwnershipFacet",
    "DiamondLoupeFacet",
]


class EngineFeatures(Enum):
    DROPPER = "DropperFacet"
    GOFP = "GOFPFacet"
    INVENTORY = "InventoryFacet"


def feature_from_facet_name(facet_name: str) -> Optional[EngineFeatures]:
    try:
        return EngineFeatures(facet_name)
    except ValueError:
        return None


FEATURE_FACETS: Dict[EngineFeatures, List[str]] = {
    EngineFeatures.DROPPER: ["DropperFacet"],
    EngineFeatures.GOFP: ["GOFPFacet"],
    EngineFeatures.INVENTORY: ["InventoryFacet"],
}

FEATURE_IGNORES: Dict[EngineFeatures, List[str]] = {
    EngineFeatures.DROPPER: {"methods": ["init"], "selectors": []},
    EngineFeatures.GOFP: {"methods": ["init"], "selectors": []},
    EngineFeatures.INVENTORY: {"methods": ["init"], "selectors": []},
}

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
    feature: Optional[EngineFeatures] = None,
    initializer_args: Optional[List[Any]] = None,
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

    facet_precedence = FACET_PRECEDENCE
    if feature is not None:
        facet_precedence = DIAMOND_FACET_PRECEDENCE + FEATURE_FACETS[feature]

    if ignore_methods is None:
        ignore_methods = []
    if ignore_selectors is None:
        ignore_selectors = []
    if methods is None:
        methods = []
    if selectors is None:
        selectors = []

    project_dir = os.path.abspath(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    )
    abis = abi.project_abis(project_dir)

    reserved_selectors: Set[str] = set()
    for facet in facet_precedence:
        facet_abi = abis.get(facet, [])
        if facet == facet_name:
            # Add feature ignores to reserved_selectors then break out of facet iteration
            facet_feature = feature_from_facet_name(facet_name)
            if facet_feature is not None:
                feature_ignores = FEATURE_IGNORES[facet_feature]
                for item in facet_abi:
                    if (
                        item["type"] == "function"
                        and item["name"] in feature_ignores["methods"]
                    ):
                        reserved_selectors.add(abi.encode_function_signature(item))

                for selector in feature_ignores["selectors"]:
                    reserved_selectors.add(selector)

            break

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
    if (
        initializer_address != ZERO_ADDRESS
        and FACET_INIT_CALLDATA.get(facet_name) is not None
    ):
        if initializer_args is None:
            initializer_args = []
        calldata = FACET_INIT_CALLDATA[facet_name](
            initializer_address, *initializer_args
        )
    transaction = diamond.diamond_cut(
        [diamond_cut_action], initializer_address, calldata, transaction_config
    )
    return transaction


def diamond_gogogo(
    owner_address: str,
    transaction_config: Dict[str, Any],
    diamond_cut_address: Optional[str] = None,
    diamond_address: Optional[str] = None,
    diamond_loupe_address: Optional[str] = None,
    ownership_address: Optional[str] = None,
    verify_contracts: Optional[bool] = False,
) -> Dict[str, Any]:
    """
    Deploy diamond along with all its basic facets and attach those facets to the diamond.

    Returns addresses of all the deployed contracts with the contract names as keys.
    """
    result: Dict[str, Any] = {"contracts": {}, "attached": []}
    if verify_contracts:
        result["verified"] = []
        result["verification_errors"] = []

    if diamond_cut_address is None:
        try:
            diamond_cut_facet = DiamondCutFacet.DiamondCutFacet(None)
            diamond_cut_facet.deploy(transaction_config)
        except Exception as e:
            print(e)
            result["error"] = "Failed to deploy DiamondCutFacet"
            return result
        result["contracts"]["DiamondCutFacet"] = diamond_cut_facet.address
    else:
        result["contracts"]["DiamondCutFacet"] = diamond_cut_address
        diamond_cut_facet = DiamondCutFacet.DiamondCutFacet(diamond_cut_address)

    if diamond_address is None:
        try:
            diamond = Diamond.Diamond(None)
            diamond.deploy(owner_address, diamond_cut_facet.address, transaction_config)
        except Exception as e:
            print(e)
            result["error"] = "Failed to deploy Diamond"
            return result
        result["contracts"]["Diamond"] = diamond.address
    else:
        result["contracts"]["Diamond"] = diamond_address
        diamond = Diamond.Diamond(diamond_address)

    if diamond_loupe_address is None:
        try:
            diamond_loupe_facet = DiamondLoupeFacet.DiamondLoupeFacet(None)
            diamond_loupe_facet.deploy(transaction_config)
        except Exception as e:
            print(e)
            result["error"] = "Failed to deploy DiamondLoupeFacet"
            return result
        result["contracts"]["DiamondLoupeFacet"] = diamond_loupe_facet.address
    else:
        result["contracts"]["DiamondLoupeFacet"] = diamond_loupe_address
        diamond_loupe_facet = DiamondLoupeFacet.DiamondLoupeFacet(diamond_loupe_address)

    if ownership_address is None:
        try:
            ownership_facet = OwnershipFacet.OwnershipFacet(None)
            ownership_facet.deploy(transaction_config)
        except Exception as e:
            print(e)
            result["error"] = "Failed to deploy OwnershipFacet"
            return result
        result["contracts"]["OwnershipFacet"] = ownership_facet.address
    else:
        result["contracts"]["OwnershipFacet"] = ownership_address
        ownership_facet = OwnershipFacet.OwnershipFacet(ownership_address)

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

    if verify_contracts:
        try:
            diamond_cut_facet.verify_contract()
            result["verified"].append("DiamondCutFacet")
        except Exception as e:
            result["verification_errors"].append(repr(e))

        try:
            diamond.verify_contract()
            result["verified"].append("Diamond")
        except Exception as e:
            result["verification_errors"].append(repr(e))

        try:
            diamond_loupe_facet.verify_contract()
            result["verified"].append("DiamondLoupeFacet")
        except Exception as e:
            result["verification_errors"].append(repr(e))

        try:
            ownership_facet.verify_contract()
        except Exception as e:
            result["verification_errors"].append(repr(e))

    return result


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
                item["tokenAmount"] *= 10**erc20_decimals
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


def lootbox_gogogo(
    terminus_address,
    admin_terminus_address,
    admin_terminus_pool_id,
    vrf_coordinator_address,
    link_token_address,
    chainlik_vrf_fee,
    chainlik_vrf_keyhash,
    tx_config,
) -> Dict[str, Any]:
    admin_terminus_contract = MockTerminus.MockTerminus(admin_terminus_address)

    print("Deploying lootbox...")
    lootbox_contract = Lootbox.Lootbox(None)
    lootbox_contract.deploy(
        terminus_address,
        admin_terminus_address,
        admin_terminus_pool_id,
        vrf_coordinator_address,
        link_token_address,
        chainlik_vrf_fee,
        chainlik_vrf_keyhash,
        tx_config,
    )

    contracts = {
        "Lootbox": {
            "Address": lootbox_contract.address,
            "TerminusAddress": terminus_address,
            "AdminTerminusAddress": admin_terminus_address,
            "AdminTokenPoolId": admin_terminus_pool_id,
        },
    }

    return contracts


def dropper_gogogo(
    admin_terminus_address: str,
    admin_terminus_pool_id: int,
    transaction_config: Dict[str, Any],
) -> Dict[str, Any]:
    deployment_info = diamond_gogogo(
        owner_address=transaction_config["from"].address,
        transaction_config=transaction_config,
    )

    dropper_facet = DropperFacet.DropperFacet(None)
    dropper_facet.deploy(transaction_config=transaction_config)
    deployment_info["contracts"]["DropperFacet"] = dropper_facet.address

    diamond_address = deployment_info["contracts"]["Diamond"]
    facet_cut(
        diamond_address,
        "DropperFacet",
        dropper_facet.address,
        "add",
        transaction_config,
        initializer_address=dropper_facet.address,
        feature=EngineFeatures.DROPPER,
        initializer_args=[admin_terminus_address, admin_terminus_pool_id],
    )
    deployment_info["attached"].append("DropperFacet")

    return deployment_info


def gofp_gogogo(
    admin_terminus_address: str,
    admin_terminus_pool_id: int,
    transaction_config: Dict[str, Any],
) -> Dict[str, Any]:
    deployment_info = diamond_gogogo(
        owner_address=transaction_config["from"].address,
        transaction_config=transaction_config,
    )

    gofp_facet = GOFPFacet.GOFPFacet(None)
    gofp_facet.deploy(transaction_config=transaction_config)
    deployment_info["contracts"]["GOFPFacet"] = gofp_facet.address

    diamond_address = deployment_info["contracts"]["Diamond"]
    facet_cut(
        diamond_address,
        "GOFPFacet",
        gofp_facet.address,
        "add",
        transaction_config,
        initializer_address=gofp_facet.address,
        feature=EngineFeatures.GOFP,
        initializer_args=[admin_terminus_address, admin_terminus_pool_id],
    )
    deployment_info["attached"].append("GOFPFacet")

    return deployment_info


def inventory_gogogo(
    admin_terminus_address: str,
    admin_terminus_pool_id: int,
    subject_erc721_address: str,
    transaction_config: Dict[str, Any],
    diamond_cut_address: Optional[str] = None,
    diamond_address: Optional[str] = None,
    diamond_loupe_address: Optional[str] = None,
    ownership_address: Optional[str] = None,
    inventory_facet_address: Optional[str] = None,
    verify_contracts: Optional[bool] = False,
) -> Dict[str, Any]:
    """
    Deploys an EIP2535 Diamond contract and an InventoryFacet and mounts the InventoryFacet onto the Diamond contract.

    Returns the addresses and attachments.
    """
    deployment_info = diamond_gogogo(
        owner_address=transaction_config["from"].address,
        transaction_config=transaction_config,
        diamond_cut_address=diamond_cut_address,
        diamond_address=diamond_address,
        diamond_loupe_address=diamond_loupe_address,
        ownership_address=ownership_address,
        verify_contracts=verify_contracts,
    )

    if inventory_facet_address is None:
        inventory_facet = InventoryFacet.InventoryFacet(None)
        inventory_facet.deploy(transaction_config=transaction_config)
    else:
        inventory_facet = InventoryFacet.InventoryFacet(inventory_facet_address)

    deployment_info["contracts"]["InventoryFacet"] = inventory_facet.address

    if verify_contracts:
        try:
            inventory_facet.verify_contract()
            deployment_info["verified"].append("InventoryFacet")
        except Exception as e:
            deployment_info["verification_errors"].append(repr(e))

    facet_cut(
        deployment_info["contracts"]["Diamond"],
        "InventoryFacet",
        inventory_facet.address,
        "add",
        transaction_config,
        initializer_address=inventory_facet.address,
        feature=EngineFeatures.INVENTORY,
        initializer_args=[
            admin_terminus_address,
            admin_terminus_pool_id,
            subject_erc721_address,
        ],
    )
    deployment_info["attached"].append("InventoryFacet")

    return deployment_info


def handle_facet_cut(args: argparse.Namespace) -> None:
    network.connect(args.network)
    diamond_address = args.address
    action = args.action
    facet_name = args.facet_name
    facet_address = args.facet_address
    transaction_config = Diamond.get_transaction_config(args)
    facet_cut(
        diamond_address,
        facet_name,
        facet_address,
        action,
        transaction_config,
        initializer_address=args.initializer_address,
        ignore_methods=args.ignore_methods,
        ignore_selectors=args.ignore_selectors,
        methods=args.methods,
        selectors=args.selectors,
    )


def handle_lootbox_gogogo(args: argparse.Namespace) -> None:
    network.connect(args.network)
    terminus_address = args.terminus_address
    transaction_config = MockTerminus.get_transaction_config(args)
    result = lootbox_gogogo(
        terminus_address,
        args.admin_terminus_address,
        args.admin_terminus_pool_id,
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


def handle_dropper_gogogo(args: argparse.Namespace) -> None:
    network.connect(args.network)
    transaction_config = MockTerminus.get_transaction_config(args)
    result = dropper_gogogo(
        args.terminus_address, args.terminus_pool_id, transaction_config
    )
    if args.outfile is not None:
        with args.outfile:
            json.dump(result, args.outfile)
    json.dump(result, sys.stdout, indent=4)


def handle_gofp_gogogo(args: argparse.Namespace) -> None:
    network.connect(args.network)
    transaction_config = MockTerminus.get_transaction_config(args)
    result = gofp_gogogo(
        args.admin_terminus_address, args.admin_terminus_pool_id, transaction_config
    )
    if args.outfile is not None:
        with args.outfile:
            json.dump(result, args.outfile)
    json.dump(result, sys.stdout, indent=4)


def handle_inventory_gogogo(args: argparse.Namespace) -> None:
    network.connect(args.network)
    transaction_config = InventoryFacet.get_transaction_config(args)
    result = inventory_gogogo(
        admin_terminus_address=args.admin_terminus_address,
        admin_terminus_pool_id=args.admin_terminus_pool_id,
        subject_erc721_address=args.subject_erc721_address,
        transaction_config=transaction_config,
        diamond_cut_address=args.diamond_cut_address,
        diamond_address=args.diamond_address,
        diamond_loupe_address=args.diamond_loupe_address,
        ownership_address=args.ownership_address,
        inventory_facet_address=args.inventory_facet_address,
        verify_contracts=args.verify_contracts,
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

    facet_cut_parser = subcommands.add_parser(
        "facet-cut",
        help="Operate on facets of a Diamond contract",
        description="Operate on facets of a Diamond contract",
    )
    Diamond.add_default_arguments(facet_cut_parser, transact=True)
    facet_cut_parser.add_argument(
        "--facet-name",
        required=True,
        choices=FACETS,
        help="Name of facet to cut into or out of diamond",
    )
    facet_cut_parser.add_argument(
        "--facet-address",
        required=False,
        default=ZERO_ADDRESS,
        help=f"Address of deployed facet (default: {ZERO_ADDRESS})",
    )
    facet_cut_parser.add_argument(
        "--action",
        required=True,
        choices=FACET_ACTIONS,
        help="Diamond cut action to take on entire facet",
    )
    facet_cut_parser.add_argument(
        "--initializer-address",
        default=ZERO_ADDRESS,
        help=f"Address of contract to run as initializer after cut (default: {ZERO_ADDRESS})",
    )
    facet_cut_parser.add_argument(
        "--ignore-methods",
        nargs="+",
        help="Names of methods to ignore when cutting a facet onto or off of the diamond",
    )
    facet_cut_parser.add_argument(
        "--ignore-selectors",
        nargs="+",
        help="Method selectors to ignore when cutting a facet onto or off of the diamond",
    )
    facet_cut_parser.add_argument(
        "--methods",
        nargs="+",
        help="Names of methods to add (if set, --ignore-methods and --ignore-selectors are not used)",
    )
    facet_cut_parser.add_argument(
        "--selectors",
        nargs="+",
        help="Selectors to add (if set, --ignore-methods and --ignore-selectors are not used)",
    )
    facet_cut_parser.set_defaults(func=handle_facet_cut)

    dropper_gogogo_parser = subcommands.add_parser(
        "dropper-gogogo",
        help="Deploy Dropper diamond contract",
        description="Deploy Dropper diamond contract",
    )
    Diamond.add_default_arguments(dropper_gogogo_parser, transact=True)
    dropper_gogogo_parser.add_argument(
        "--terminus-address",
        required=True,
        help="Address of Terminus contract defining access control for this Dropper contract",
    )
    dropper_gogogo_parser.add_argument(
        "--terminus-pool-id",
        required=True,
        type=int,
        help="Pool ID of Terminus pool for administrators of this dropper contract",
    )
    dropper_gogogo_parser.add_argument(
        "-o",
        "--outfile",
        type=argparse.FileType("w"),
        default=None,
        help="(Optional) file to write deployed addresses to",
    )
    dropper_gogogo_parser.set_defaults(func=handle_dropper_gogogo)

    gofp_gogogo_parser = subcommands.add_parser(
        "gofp-gogogo",
        help="Deploy gofp diamond contract",
        description="Deploy gofp diamond contract",
    )
    Diamond.add_default_arguments(gofp_gogogo_parser, transact=True)
    gofp_gogogo_parser.add_argument(
        "--admin-terminus-address",
        required=True,
        help="Address of Terminus contract defining access control for this GardenOfForkingPaths contract",
    )
    gofp_gogogo_parser.add_argument(
        "--admin-terminus-pool-id",
        required=True,
        type=int,
        help="Pool ID of Terminus pool for administrators of this GardenOfForkingPaths contract",
    )
    gofp_gogogo_parser.add_argument(
        "-o",
        "--outfile",
        type=argparse.FileType("w"),
        default=None,
        help="(Optional) file to write deployed addresses to",
    )
    gofp_gogogo_parser.set_defaults(func=handle_gofp_gogogo)

    inventory_gogogo_parser = subcommands.add_parser(
        "inventory-gogogo",
        description="Deploy Inventory diamond contract",
    )
    Diamond.add_default_arguments(inventory_gogogo_parser, transact=True)
    inventory_gogogo_parser.add_argument(
        "--verify-contracts",
        action="store_true",
        help="Verify contracts",
    )
    inventory_gogogo_parser.add_argument(
        "--admin-terminus-address",
        required=True,
        help="Address of Terminus contract defining access control for this GardenOfForkingPaths contract",
    )
    inventory_gogogo_parser.add_argument(
        "--admin-terminus-pool-id",
        required=True,
        type=int,
        help="Pool ID of Terminus pool for administrators of this GardenOfForkingPaths contract",
    )
    inventory_gogogo_parser.add_argument(
        "--subject-erc721-address",
        required=True,
        help="Address of ERC721 contract that the Inventory modifies",
    )
    inventory_gogogo_parser.add_argument(
        "--diamond-cut-address",
        required=False,
        default=None,
        help="Address to deployed DiamondCutFacet. If provided, this command skips deployment of a new DiamondCutFacet.",
    )
    inventory_gogogo_parser.add_argument(
        "--diamond-address",
        required=False,
        default=None,
        help="Address to deployed Diamond contract. If provided, this command skips deployment of a new Diamond contract and simply mounts the required facets onto the existing Diamond contract. Assumes that there is no collision of selectors.",
    )
    inventory_gogogo_parser.add_argument(
        "--diamond-loupe-address",
        required=False,
        default=None,
        help="Address to deployed DiamondLoupeFacet. If provided, this command skips deployment of a new DiamondLoupeFacet. It mounts the existing DiamondLoupeFacet onto the Diamond.",
    )
    inventory_gogogo_parser.add_argument(
        "--ownership-address",
        required=False,
        default=None,
        help="Address to deployed OwnershipFacet. If provided, this command skips deployment of a new OwnershipFacet. It mounts the existing OwnershipFacet onto the Diamond.",
    )
    inventory_gogogo_parser.add_argument(
        "--inventory-facet-address",
        required=False,
        default=None,
        help="Address to deployed InventoryFacet. If provided, this command skips deployment of a new InventoryFacet. It mounts the existing InventoryFacet onto the Diamond.",
    )
    inventory_gogogo_parser.add_argument(
        "-o",
        "--outfile",
        type=argparse.FileType("w"),
        default=None,
        help="(Optional) file to write deployed addresses to",
    )
    inventory_gogogo_parser.set_defaults(func=handle_inventory_gogogo)

    lootbox_gogogo_parser = subcommands.add_parser(
        "lootbox-gogogo",
        help="Deploys Lootbox contract",
        description="Deploys Lootbox contract",
    )

    lootbox_gogogo_parser.add_argument(
        "-o",
        "--outfile",
        type=argparse.FileType("w"),
        default=None,
        help="(Optional) file to write deployed addresses to",
    )

    lootbox_gogogo_parser.add_argument(
        "--terminus-address",
        type=str,
        required=True,
        help="Address of the terminus contract",
    )

    lootbox_gogogo_parser.add_argument(
        "--admin-terminus-address",
        required=True,
        help="Address of Terminus contract defining access control for this Lootbox contract",
    )
    lootbox_gogogo_parser.add_argument(
        "--admin-terminus-pool-id",
        required=True,
        type=int,
        help="Pool ID of Terminus pool for administrators of this Lootbox contract",
    )

    lootbox_gogogo_parser.add_argument(
        "--vrf-coordinator-address",
        type=str,
        required=True,
        help="Address of the vrf coordinator contract",
    )

    lootbox_gogogo_parser.add_argument(
        "--link-token-address",
        type=str,
        required=True,
        help="Address of the link token contract",
    )

    lootbox_gogogo_parser.add_argument(
        "--chainlik-vrf-fee",
        type=int,
        required=True,
        help="Chainlink vrf fee",
    )

    lootbox_gogogo_parser.add_argument(
        "--chainlik-vrf-keyhash",
        type=str,
        required=True,
        help="Chainlink vrf keyhash",
    )

    MockTerminus.add_default_arguments(lootbox_gogogo_parser, transact=True)

    lootbox_gogogo_parser.set_defaults(func=handle_lootbox_gogogo)

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
