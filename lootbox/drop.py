"""
Lootbox drop operations
"""

import argparse
import csv
import json
import os
import sys

from brownie import network
from tqdm import tqdm

from . import Lootbox


def checkpoint_key(address, lootbox_id):
    return f"{address}-{lootbox_id}"


def is_contract(address):
    address_is_contract = network.web3.eth.getCode(address)
    if address_is_contract == "0x":
        return False
    elif address_is_contract == "0x0":  # ganache
        return False
    else:
        return True


def load_drop_matrix_from_csv(infile, checkpoint_file):
    """
    Input is a CSV file with an "Address" column containing addresses to drop to.
    Each other column has a lootbox ID as its column heading.
    For an address a and a lootbox ID i, the entry for (a, i) is the number of lootboxes of type i that
    should be minted to a.

    Output of this function is of the form:
    {
        <lootbox_id_1>: {
            "<address_1>": <amount>,
            ...
        },
        ...
    }

    Checkpoints will be of the form:
    {
        "<address>-<lootbox_id>": [[<amount_1>, "<txhash_1>"], ...],
        ...
    }

    When we load the input file, we will check it against the checkpoint. We reduce the amount of drops
    for each (address, lootbox ID) pair based on the total amount dropped in the checkpoint file for that pair.
    """
    checkpoint = {}
    try:
        with open(checkpoint_file, "r") as ifp:
            checkpoint = json.load(ifp)
    except:
        with open(checkpoint_file, "w") as ofp:
            json.dump(checkpoint, ofp)

    result = {}
    with open(infile, "r") as ifp:
        reader = csv.reader(ifp)
        header = next(reader)
        lootbox_id_indices = {}
        address_index = -1
        for i, colname in enumerate(header):
            if colname.lower().strip() == "address":
                assert address_index < 0
                address_index = i
            else:
                lootbox_id = int(colname.strip())
                lootbox_id_indices[lootbox_id] = i
                result[lootbox_id] = {}
        assert address_index >= 0, "No address column found"

        for row in reader:
            for lootbox_id, index in lootbox_id_indices.items():
                address = row[address_index]
                raw_amount = row[index].strip()
                if raw_amount == "" or raw_amount == "0":
                    continue
                amount = int(raw_amount)

                if result[lootbox_id].get(address) is None:
                    result[lootbox_id][address] = 0
                result[lootbox_id][address] += amount
                if result[lootbox_id][address] <= 0:
                    del result[lootbox_id][address]

    return result


def execute_drop(
    job_spec,
    checkpoint_file,
    errors_file,
    lootbox: Lootbox.Lootbox,
    batch_size,
    transaction_config,
):
    checkpoint = {}
    with open(checkpoint_file, "r") as ifp:
        checkpoint = json.load(ifp)

    errors = []
    if not os.path.isfile(errors_file):
        with open(errors_file, "w") as ofp:
            json.dump(errors, ofp)
    else:
        with open(errors_file, "r") as ifp:
            errors = json.load(ifp)

    if errors:
        failed_jobs = {}
        for lootbox_id, batch, amount in errors:
            if failed_jobs.get(lootbox_id) is None:
                failed_jobs[lootbox_id] = {}
            for address in batch:
                failed_jobs[lootbox_id][address] = amount

    for lootbox_id, item in job_spec.items():
        jobs_by_amount = {}
        for address, amount in item.items():

            # Get checkpointed part of drop balance
            checkpoint_ops = checkpoint.get(checkpoint_key(address, lootbox_id))
            if checkpoint_ops is None:
                checkpoint_ops = []
            checkpoint_amount = 0

            for _amount, _ in checkpoint_ops:
                checkpoint_amount += _amount

            # Get errors part of drop balance
            errors_amount = 0

            if lootbox_id in failed_jobs:
                if jobs_by_amount[lootbox_id].get(address) is not None:
                    errors_amount += failed_jobs[lootbox_id][address]

            # Real drop amount
            drop_amount = amount - checkpoint_amount - errors_amount

            if drop_amount > 0:
                if jobs_by_amount.get(drop_amount) is None:
                    jobs_by_amount[drop_amount] = []
                jobs_by_amount[drop_amount].append(address)

        for amount, addresses in jobs_by_amount.items():
            num_batches = int(len(addresses) / batch_size)
            if len(addresses) > num_batches * batch_size:
                num_batches += 1

            current_index = 0
            for _ in tqdm(
                range(num_batches),
                desc=f"Processing amount: {amount} for lootbox: {lootbox_id} with batch size: {batch_size}",
            ):
                batch = addresses[current_index : current_index + batch_size]
                try:
                    # apply check logic here

                    receipt = lootbox.batch_mint_lootboxes_constant(
                        lootbox_id, batch, amount, transaction_config
                    )
                    transaction_hash = receipt.txid

                    for address in batch:
                        key = checkpoint_key(address, lootbox_id)
                        if checkpoint.get(key) is None:
                            checkpoint[key] = []
                        checkpoint[key].append([amount, transaction_hash])
                    with open(checkpoint_file, "w") as ofp:
                        json.dump(checkpoint, ofp)
                except Exception as e:
                    print("Error submitting transaction:")
                    print(e)
                    errors.append([lootbox_id, batch, amount])
                    with open(errors_file, "w") as ofp:
                        json.dump(errors, ofp)
                current_index = current_index + batch_size

    return checkpoint


def retry_drop(
    job_spec, checkpoint_file, errors_file, lootbox, batch_size, transaction_config,
):

    checkpoint = {}
    with open(checkpoint_file, "r") as ifp:
        checkpoint = json.load(ifp)

    errors = []
    if not os.path.isfile(errors_file):
        raise "Don't have errors file"
    else:
        with open(errors_file, "r") as ifp:
            errors = json.load(ifp)

    retry_jobs = {}

    for lootbox_id, batch, amount in errors:
        if retry_jobs.get(lootbox_id) is None:
            retry_jobs[lootbox_id] = {}
        for address in batch:
            retry_jobs[lootbox_id][address] = amount

    for lootbox_id, item in retry_jobs.items():
        jobs_by_amount = {}
        for address, amount in item.items():

            # Get checkpointed part of drop balance
            checkpoint_ops = checkpoint.get(checkpoint_key(address, lootbox_id))
            if checkpoint_ops is None:
                checkpoint_ops = []
            checkpoint_amount = 0

            for _amount, _ in checkpoint_ops:
                checkpoint_amount += _amount

            # Get errors part of drop balance

            tasks_amount += job_spec[lootbox_id][address]

            # Real drop amount
            drop_amount = tasks_amount - checkpoint_amount

            if drop_amount == amount:
                if jobs_by_amount.get(drop_amount) is None:
                    jobs_by_amount[drop_amount] = []
                jobs_by_amount[drop_amount].append(address)

        for amount, addresses in jobs_by_amount.items():
            num_batches = int(len(addresses) / batch_size)
            if len(addresses) > num_batches * batch_size:
                num_batches += 1

            current_index = 0
            for _ in tqdm(
                range(num_batches),
                desc=f"Processing amount: {amount} for lootbox: {lootbox_id} with batch size: {batch_size}",
            ):
                batch = addresses[current_index : current_index + batch_size]
                try:
                    # apply check logic here

                    receipt = lootbox.batch_mint_lootboxes_constant(
                        lootbox_id, batch, amount, transaction_config
                    )
                    transaction_hash = receipt.txid

                    for address in batch:
                        key = checkpoint_key(address, lootbox_id)
                        if checkpoint.get(key) is None:
                            checkpoint[key] = []
                        checkpoint[key].append([amount, transaction_hash])
                    with open(checkpoint_file, "w") as ofp:
                        json.dump(checkpoint, ofp)
                except Exception as e:
                    print("Error submitting transaction:")
                    print(e)
                    errors.append([lootbox_id, batch, amount])
                    with open(errors_file, "w") as ofp:
                        json.dump(errors, ofp)
                current_index = current_index + batch_size


def handle_make(args: argparse.Namespace) -> None:
    result = load_drop_matrix_from_csv(args.infile, args.checkpoint)
    with args.outfile:
        json.dump(result, args.outfile)


def handle_execute(args: argparse.Namespace) -> None:
    network.connect(args.network)
    lootbox = Lootbox.Lootbox(args.address)
    transaction_config = Lootbox.get_transaction_config(args)

    with args.infile:
        job_spec = json.load(args.infile)
    execute_drop(
        job_spec,
        args.checkpoint,
        args.errors,
        lootbox,
        args.batch_size,
        transaction_config,
    )


def handle_retry(args: argparse.Namespace) -> None:
    network.connect(args.network)
    lootbox = Lootbox.Lootbox(args.address)
    transaction_config = Lootbox.get_transaction_config(args)

    with args.infile:
        job_spec = json.load(args.infile)
    retry_drop(
        job_spec,
        args.checkpoint,
        args.errors,
        lootbox,
        args.batch_size,
        transaction_config,
    )


def generate_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Lootbox drops")
    parser.set_defaults(func=lambda _: parser.print_help())
    subparsers = parser.add_subparsers()

    make_parser = subparsers.add_parser("make")
    make_parser.add_argument(
        "-i", "--infile", type=str, required=True, help="Path to input CSV"
    )
    make_parser.add_argument(
        "-c",
        "--checkpoint",
        type=str,
        required=True,
        help="Path to checkpoint file (JSON format); file will be created if it does not exist",
    )
    make_parser.add_argument(
        "-o",
        "--outfile",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Path to output JSON (will be created); if not specified, writes to stdout",
    )
    make_parser.set_defaults(func=handle_make)

    execute_parser = subparsers.add_parser("execute")
    Lootbox.add_default_arguments(execute_parser, transact=True)
    execute_parser.add_argument(
        "-i",
        "--infile",
        type=argparse.FileType("r"),
        required=True,
        help="Job file (JSON)",
    )
    execute_parser.add_argument(
        "-c",
        "--checkpoint",
        type=str,
        required=True,
        help="Path to checkpoint file (JSON format); file will be created if it does not exist",
    )
    execute_parser.add_argument(
        "-e",
        "--errors",
        type=str,
        required=True,
        help="Path to errors file (JSON format); file will be created if it does not exist",
    )
    execute_parser.add_argument(
        "-N",
        "--batch-size",
        type=int,
        required=True,
        help="Number of addresses to process per transaction",
    )
    execute_parser.set_defaults(func=handle_execute)

    execute_parser = subparsers.add_parser("retry")
    Lootbox.add_default_arguments(execute_parser, transact=True)
    execute_parser.add_argument(
        "-i",
        "--infile",
        type=argparse.FileType("r"),
        required=True,
        help="Job file (JSON)",
    )
    execute_parser.add_argument(
        "-i",
        "--errors",
        type=argparse.FileType("r"),
        required=True,
        help="Path to errors file (JSON format);",
    )
    execute_parser.add_argument(
        "-c",
        "--checkpoint",
        type=str,
        required=True,
        help="Path to checkpoint file (JSON format); file will be created if it does not exist",
    )
    execute_parser.add_argument(
        "-N",
        "--batch-size",
        type=int,
        required=True,
        help="Number of addresses to process per transaction",
    )
    execute_parser.set_defaults(func=handle_execute)

    return parser


def main():
    parser = generate_cli()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
