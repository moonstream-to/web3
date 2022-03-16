import argparse
import json
from typing import Any, Dict

from lootbox.MockErc20 import MockErc20

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


def gogogo(terminus_address, deployer) -> Dict[str, Any]:

    terminus_contract = MockTerminus.MockTerminus(terminus_address)

    terminus_payment_token_address = terminus_contract.payment_token()
    terminus_payment_token = MockErc20(terminus_payment_token_address)

    pool_base_price = terminus_contract.pool_base_price()
    deployer_payment_token_balance = terminus_payment_token.balance_of(deployer)

    if deployer_payment_token_balance < pool_base_price:
        raise Exception(
            f"Deployer does not have enough tokens to create terminus pool."
            f"Need {pool_base_price} but only have {deployer_payment_token_balance}"
        )

    print("Approving deployer to spend tokens to create terminus pool...")
    terminus_payment_token.approve(
        terminus_address, pool_base_price, {"from": deployer}
    )

    print("Creating terminus pool...")
    terminus_contract.create_pool_v1(pool_base_price, False, True, {"from": deployer})

    admin_token_pool_id = terminus_contract.total_pools()

    print("Deploying lootbox...")
    lootbox_contract = Lootbox.Lootbox(None)
    lootbox_contract.deploy(terminus_address, admin_token_pool_id, {"from": deployer})

    print("Setting pool controller...")
    terminus_contract.set_pool_controller(
        admin_token_pool_id, lootbox_contract.address, {"from": deployer}
    )

    contracts = {
        "Lootbox": lootbox_contract.address,
        "adminTokenPoolId": admin_token_pool_id,
    }

    return contracts
