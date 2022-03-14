import argparse
import json

from . import Lootbox


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


# def handle
