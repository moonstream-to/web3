import argparse
from ast import arg
import csv
import json
import logging
from uuid import UUID

from brownie import network
from engineapi.models import Leaderboard

from . import actions
from . import db
from . import signatures
from . import data
from . import Lootbox, core, drop, MockErc20, Dropper, auth, MockTerminus
from .settings import BLOCKCHAINS_TO_BROWNIE_NETWORKS
from .models import DropperClaim, DropperContract


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def signing_server_list_handler(args: argparse.Namespace) -> None:
    try:
        instances = signatures.list_signing_instances(
            signing_instances=[] if args.instance is None else [args.instance]
        )
    except Exception as err:
        logger.error(f"Unhandled /list exception: {err}")
        return

    print(data.SignerListResponse(instances=instances).json())


def signing_server_wakeup_handler(args: argparse.Namespace) -> None:
    try:
        run_instances = signatures.wakeup_signing_instances(
            run_confirmed=args.confirmed, dry_run=args.dry_run
        )
    except signatures.AWSRunInstancesFail:
        return
    except Exception as err:
        logger.error(f"Unhandled /wakeup exception: {err}")
        return

    print(data.SignerWakeupResponse(instances=run_instances).json())


def signing_server_sleep_handler(args: argparse.Namespace) -> None:
    try:
        terminated_instances = signatures.sleep_signing_instances(
            signing_instances=[args.instance],
            termination_confirmed=args.confirmed,
            dry_run=args.dry_run,
        )
    except signatures.AWSDescribeInstancesFail:
        return
    except signatures.SigningInstancesNotFound:
        return
    except signatures.SigningInstancesTerminationLimitExceeded:
        return
    except signatures.AWSTerminateInstancesFail:
        return
    except Exception as err:
        logger.error(f"Unhandled /sleep exception: {err}")
        return

    print(data.SignerSleepResponse(instances=list(terminated_instances)).json())


def create_dropper_contract_handler(args: argparse.Namespace) -> None:
    try:
        with db.yield_db_session_ctx() as db_session:
            created_contract = actions.create_dropper_contract(
                db_session=db_session,
                blockchain=args.blockchain,
                dropper_contract_address=args.address,
                title=args.title,
                description=args.description,
                image_uri=args.image_uri,
            )
    except Exception as err:
        logger.error(f"Unhandled /create_dropper_contract exception: {err}")
        return
    print(created_contract)


def delete_dropper_contract_handler(args: argparse.Namespace) -> None:
    try:
        with db.yield_db_session_ctx() as db_session:
            removed_contract = actions.delete_dropper_contract(
                db_session=db_session,
                blockchain=args.blockchain,
                dropper_contract_address=args.address,
            )
    except Exception as err:
        logger.error(f"Unhandled /delete_dropper_contract exception: {err}")
        return
    print(removed_contract)


def list_dropper_contracts_handler(args: argparse.Namespace) -> None:
    try:
        with db.yield_db_session_ctx() as db_session:
            results = actions.list_dropper_contracts(
                db_session=db_session, blockchain=args.blockchain
            )
    except Exception as err:
        logger.error(f"Unhandled /list_dropper_contracts exception: {err}")
        return
    print(
        "\n".join(
            [
                data.DropperContractResponse(
                    id=result.id,
                    blockchain=result.blockchain,
                    address=result.address,
                    title=result.title,
                    description=result.description,
                    image_uri=result.image_uri,
                ).json()
                for result in results
            ]
        )
    )


def dropper_create_drop_handler(args: argparse.Namespace) -> None:
    try:
        with db.yield_db_session_ctx() as db_session:
            created_claim = actions.create_claim(
                db_session=db_session,
                dropper_contract_id=args.dropper_contract_id,
                claim_id=args.claim_id,
                title=args.title,
                description=args.description,
                terminus_address=args.terminus_address,
                terminus_pool_id=args.terminus_pool_id,
                claim_block_deadline=args.block_deadline,
            )
    except Exception as err:
        logger.error(f"Unhandled /create_dropper_claim exception: {err}")
        return
    print(created_claim)


def dropper_activate_drop_handler(args: argparse.Namespace) -> None:
    try:
        with db.yield_db_session_ctx() as db_session:
            activated_claim = actions.activate_claim(
                db_session=db_session,
                dropper_claim_id=args.dropper_claim_id,
            )
    except Exception as err:
        logger.error(f"Unhandled exception: {err}")
        return
    print(activated_claim)


def dropper_deactivate_drop_handler(args: argparse.Namespace) -> None:
    try:
        with db.yield_db_session_ctx() as db_session:
            deactivated_claim = actions.deactivate_claim(
                db_session=db_session,
                dropper_claim_id=args.dropper_claim_id,
            )
    except Exception as err:
        logger.error(f"Unhandled exception: {err}")
        return
    print(deactivated_claim)


def dropper_admin_pool_handler(args: argparse.Namespace) -> None:
    try:
        with db.yield_db_session_ctx() as db_session:
            (
                blockchain,
                terminus_address,
                terminus_pool_id,
            ) = actions.get_claim_admin_pool(
                db_session=db_session, dropper_claim_id=args.id
            )
    except Exception as err:
        logger.error(f"Unhandled exception: {err}")
        return

    print(
        f"Blockchain: {blockchain}, Terminus address: {terminus_address}, Pool ID: {terminus_pool_id}"
    )


def dropper_list_drops_handler(args: argparse.Namespace) -> None:
    try:
        with db.yield_db_session_ctx() as db_session:
            dropper_claims = actions.list_claims(
                db_session=db_session,
                dropper_contract_id=args.dropper_contract_id,
                active=args.active,
            )
    except Exception as err:
        logger.error(f"Unhandled /list_dropper_claims exception: {err}")
        return
    print(dropper_claims)


def dropper_delete_drop_handler(args: argparse.Namespace) -> None:
    try:
        with db.yield_db_session_ctx() as db_session:
            removed_claim = actions.delete_claim(
                db_session=db_session,
                dropper_claim_id=args.dropper_claim_id,
            )
    except Exception as err:
        logger.error(f"Unhandled /delete_dropper_claim exception: {err}")
        return
    print(removed_claim)


def add_claimants_handler(args: argparse.Namespace) -> None:

    """
    Load list of claimats from csv file and add them to the database.
    """

    claimants = []

    with open(args.claimants_file, "r") as f:

        reader = csv.DictReader(f)

        for row in reader:

            if len(row) != 2:
                logger.error(f"Invalid row: {row}")
                raise Exception("Invalid row")
            claimants.append({"address": row["address"], "amount": row["amount"]})

    # format as DropAddClaimantsRequest

    claimants = data.DropAddClaimantsRequest(
        dropper_claim_id=args.dropper_claim_id, claimants=claimants
    )

    with db.yield_db_session_ctx() as db_session:

        try:
            claimants = actions.add_claimants(
                db_session=db_session,
                dropper_claim_id=claimants.dropper_claim_id,
                claimants=claimants.claimants,
                added_by="cli",
            )
        except Exception as err:
            logger.error(f"Unhandled /add_claimants exception: {err}")
            return
    print(data.ClaimantsResponse(claimants=claimants).json())


def delete_claimants_handler(args: argparse.Namespace) -> None:
    """
    Read csv file and remove addresses in that list from claim
    """

    import csv

    addresses = []

    with open(args.claimants_file, "r") as f:

        reader = csv.DictReader(f)

        for row in reader:

            if len(row) != 1:
                logger.error(f"Invalid row: {row}")
                raise Exception("Invalid row")
            addresses.append(row["address"])

    # format as DropRemoveClaimantsRequest

    removing_addresses = data.DropRemoveClaimantsRequest(
        dropper_claim_id=args.dropper_claim_id, addresses=addresses
    )

    with db.yield_db_session_ctx() as db_session:

        try:
            addresses = actions.delete_claimants(
                db_session=db_session,
                dropper_claim_id=removing_addresses.dropper_claim_id,
                addresses=removing_addresses.addresses,
            )
        except Exception as err:
            logger.error(f"Unhandled /delete_claimants exception: {err}")
            return
    print(data.RemoveClaimantsResponse(addresses=addresses).json())


def list_claimants_handler(args: argparse.Namespace) -> None:
    """
    List claimants for a claim
    """

    with db.yield_db_session_ctx() as db_session:

        try:
            claimants = actions.get_claimants(
                db_session=db_session, dropper_claim_id=args.dropper_claim_id
            )
        except Exception as err:
            logger.error(f"Unhandled /list_claimants exception: {err}")
            return
    print(claimants)


def add_scores_handler(args: argparse.Namespace) -> None:

    scores = []

    with open(args.input_file, "r") as f:

        json_input = json.load(f)

        with db.yield_db_session_ctx() as db_session:

            try:
                scores = actions.add_scores(
                    db_session=db_session,
                    leaderboard_id=args.leaderboard_id,
                    scores=json_input,
                )
            except Exception as err:
                logger.error(f"Unhandled /add_scores exception: {err}")
                return


def list_leaderboards_handler(args: argparse.Namespace) -> None:

    with db.yield_db_session_ctx() as db_session:
        Leaderboards = actions.list_leaderboards(
            db_session=db_session,
            limit=args.limit,
            offset=args.offset,
        )

        print(Leaderboards)


def create_leaderboard_handler(args: argparse.Namespace) -> None:

    with db.yield_db_session_ctx() as db_session:
        Leaderboard = actions.create_leaderboard(
            db_session=db_session,
            title=args.title,
            description=args.description,
        )

        print(Leaderboard)


def claimant_signature_refetch_handler(args: argparse.Namespace) -> None:

    with db.yield_db_session_ctx() as db_session:

        blockchain = (
            db_session.query(DropperContract.blockchain)
            .join(DropperClaim, DropperClaim.dropper_contract_id == DropperContract.id)
            .filter(DropperClaim.id == UUID(args.dropper_claim_id))
        ).one()

        network.connect(BLOCKCHAINS_TO_BROWNIE_NETWORKS[blockchain.blockchain])

        updated_amount = actions.refetch_drop_signatures(
            db_session=db_session, dropper_claim_id=args.dropper_claim_id
        )

        print(f"Amount of updated claimants: {updated_amount}")


def main() -> None:

    parser = argparse.ArgumentParser(
        description="dao: The command line interface to Moonstream DAO"
    )
    parser.set_defaults(func=lambda _: parser.print_help())
    subparsers = parser.add_subparsers()

    lootbox_parser = Lootbox.generate_cli()
    subparsers.add_parser("lootbox", parents=[lootbox_parser], add_help=False)

    dropper_parser = Dropper.generate_cli()
    subparsers.add_parser("dropper", parents=[dropper_parser], add_help=False)

    core_parser = core.generate_cli()
    subparsers.add_parser("core", parents=[core_parser], add_help=False)

    erc20_parser = MockErc20.generate_cli()
    subparsers.add_parser("mock-erc20", parents=[erc20_parser], add_help=False)

    drop_parser = drop.generate_cli()
    subparsers.add_parser("drop", parents=[drop_parser], add_help=False)

    terminus_parser = MockTerminus.generate_cli()
    subparsers.add_parser("terminus", parents=[terminus_parser], add_help=False)

    # Signing server parser
    parser_signing_server = subparsers.add_parser(
        "signing", description="Signing server commands"
    )
    parser_signing_server.set_defaults(
        func=lambda _: parser_signing_server.print_help()
    )
    subparsers_signing_server = parser_signing_server.add_subparsers(
        description="Signing server commands"
    )

    parser_signing_server_list = subparsers_signing_server.add_parser(
        "list", description="List signing servers"
    )
    parser_signing_server_list.add_argument(
        "-i",
        "--instance",
        type=str,
        help="Instance id to get",
    )
    parser_signing_server_list.set_defaults(func=signing_server_list_handler)

    parser_signing_server_wakeup = subparsers_signing_server.add_parser(
        "wakeup", description="Run signing server"
    )
    parser_signing_server_wakeup.add_argument(
        "-c",
        "--confirmed",
        action="store_true",
        help="Provide confirmation flag to run signing instance",
    )
    parser_signing_server_wakeup.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Dry-run flag simulate instance start, using to check proper permissions",
    )
    parser_signing_server_wakeup.set_defaults(func=signing_server_wakeup_handler)

    parser_signing_server_sleep = subparsers_signing_server.add_parser(
        "sleep", description="Terminate signing server"
    )
    parser_signing_server_sleep.add_argument(
        "-i",
        "--instance",
        type=str,
        required=True,
        help="Instance id to terminate",
    )
    parser_signing_server_sleep.add_argument(
        "-c",
        "--confirmed",
        action="store_true",
        help="Provide confirmation flag to terminate signing instance",
    )
    parser_signing_server_sleep.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Dry-run flag simulate instance termination, using to check proper permissions",
    )
    parser_signing_server_sleep.set_defaults(func=signing_server_sleep_handler)

    # Auth parser
    auth_parser = auth.generate_cli()
    subparsers.add_parser("auth", parents=[auth_parser], add_help=False)

    # engine-database parser
    parser_engine_database = subparsers.add_parser(
        "engine-db", description="engine-db commands"
    )
    parser_engine_database.set_defaults(
        func=lambda _: parser_engine_database.print_help()
    )
    subparsers_engine_database = parser_engine_database.add_subparsers(
        description="Engine-db commands"
    )

    parser_leaderboard = subparsers_engine_database.add_parser(
        "leaderboard", description="Leaderboard db commands"
    )
    parser_leaderboard.set_defaults(func=lambda _: parser_dropper.print_help())

    subparsers_leaderboard = parser_leaderboard.add_subparsers(
        description="Leaderboard db commands"
    )

    parser_leaderboard_create = subparsers_leaderboard.add_parser(
        "create-leaderboard", description="Create dropper contract"
    )
    parser_leaderboard_create.add_argument(
        "-t",
        "--title",
        type=str,
        required=False,
        help="Leaderboard title",
    )
    parser_leaderboard_create.add_argument(
        "-d",
        "--description",
        type=str,
        required=False,
        help="Leaderboard description",
    )

    parser_leaderboard_create.set_defaults(func=create_leaderboard_handler)

    parser_leaderboards_list = subparsers_leaderboard.add_parser(
        "list-leaderboards", description="List leaderboards"
    )
    parser_leaderboards_list.add_argument(
        "--limit",
        type=int,
        default=10,
    )
    parser_leaderboards_list.add_argument("--offset", type=int, default=0)
    parser_leaderboards_list.set_defaults(func=list_leaderboards_handler)

    parser_leaderboard_score = subparsers_leaderboard.add_parser(
        "add-scores", description="Add position to leaderboards score"
    )

    parser_leaderboard_score.add_argument(
        "--leaderboard-id",
        type=str,
        required=True,
        help="Contract description",
    )
    parser_leaderboard_score.add_argument(
        "--input-file",
        type=str,
        required=True,
        help="File with scores",
    )

    parser_leaderboard_score.set_defaults(func=add_scores_handler)

    parser_dropper = subparsers_engine_database.add_parser(
        "dropper", description="Dropper db commands"
    )
    parser_dropper.set_defaults(func=lambda _: parser_dropper.print_help())

    subparsers_dropper = parser_dropper.add_subparsers(
        description="Dropper db commands"
    )

    parser_dropper_contract_create = subparsers_dropper.add_parser(
        "create-contract", description="Create dropper contract"
    )
    parser_dropper_contract_create.add_argument(
        "-b",
        "--blockchain",
        type=str,
        required=True,
        help="Blockchain in wich contract was deployed",
    )
    parser_dropper_contract_create.add_argument(
        "-a",
        "--address",
        type=str,
        required=True,
        help="Contract address",
    )
    parser_dropper_contract_create.add_argument(
        "-t",
        "--title",
        type=str,
        required=False,
        help="Contract title",
    )
    parser_dropper_contract_create.add_argument(
        "-d",
        "--description",
        type=str,
        required=False,
        help="Contract description",
    )
    parser_dropper_contract_create.add_argument(
        "-i",
        "--image-uri",
        type=str,
        required=False,
        help="Contract image uri",
    )

    parser_dropper_contract_create.set_defaults(func=create_dropper_contract_handler)

    parser_dropper_contract_list = subparsers_dropper.add_parser(
        "list-contracts", description="List dropper contracts"
    )
    parser_dropper_contract_list.add_argument(
        "-b",
        "--blockchain",
        type=str,
        required=True,
        help="Blockchain in wich contract was deployed",
    )
    parser_dropper_contract_list.set_defaults(func=list_dropper_contracts_handler)

    parser_dropper_contract_delete = subparsers_dropper.add_parser(
        "delete-contract", description="Delete dropper contract"
    )
    parser_dropper_contract_delete.add_argument(
        "-b",
        "--blockchain",
        type=str,
        required=True,
        help="Blockchain in wich contract was deployed",
    )
    parser_dropper_contract_delete.add_argument(
        "-a",
        "--address",
        type=str,
        required=True,
        help="Contract address",
    )
    parser_dropper_contract_delete.set_defaults(func=delete_dropper_contract_handler)

    parser_dropper_create_drop = subparsers_dropper.add_parser(
        "create-drop", description="Create dropper drop"
    )
    parser_dropper_create_drop.add_argument(
        "-c",
        "--dropper-contract-id",
        type=str,
        required=True,
        help="Dropper contract id",
    )
    parser_dropper_create_drop.add_argument(
        "-t",
        "--title",
        type=str,
        required=True,
        help="Drop title",
    )
    parser_dropper_create_drop.add_argument(
        "-d",
        "--description",
        type=str,
        required=True,
        help="Drop description",
    )
    parser_dropper_create_drop.add_argument(
        "-b",
        "--block-deadline",
        type=int,
        required=True,
        help="Block deadline at which signature will be not returned",
    )
    parser_dropper_create_drop.add_argument(
        "-T",
        "--terminus-address",
        type=str,
        required=True,
        help="Terminus address",
    )
    parser_dropper_create_drop.add_argument(
        "-p",
        "--terminus-pool-id",
        type=int,
        required=True,
        help="Terminus pool id",
    )
    parser_dropper_create_drop.add_argument(
        "-m",
        "--claim-id",
        type=int,
        help="Claim id",
    )

    parser_dropper_create_drop.set_defaults(func=dropper_create_drop_handler)

    parser_dropper_activate_drop = subparsers_dropper.add_parser(
        "activate-drop", description="Activate dropper drop"
    )
    parser_dropper_activate_drop.add_argument(
        "-c",
        "--dropper-claim-id",
        type=str,
        required=True,
        help="Dropper claim id",
    )
    parser_dropper_activate_drop.set_defaults(func=dropper_activate_drop_handler)

    parser_dropper_deactivate_drop = subparsers_dropper.add_parser(
        "deactivate-drop", description="Deactivate dropper drop"
    )
    parser_dropper_deactivate_drop.add_argument(
        "-c",
        "--dropper-claim-id",
        type=str,
        required=True,
        help="Dropper claim id",
    )
    parser_dropper_deactivate_drop.set_defaults(func=dropper_deactivate_drop_handler)

    parser_dropper_get_claim_admin_pool = subparsers_dropper.add_parser(
        "admin-pool", description="Get admin pool for drop"
    )
    parser_dropper_get_claim_admin_pool.add_argument(
        "-i", "--id", required=True, help="Dropper Claim ID (Database ID)"
    )
    parser_dropper_get_claim_admin_pool.set_defaults(func=dropper_admin_pool_handler)

    parser_dropper_list_drops = subparsers_dropper.add_parser(
        "list-drops", description="List dropper drops"
    )
    parser_dropper_list_drops.add_argument(
        "-a",
        "--active",
        type=bool,
        required=True,
        help="Claim is active flag",
    )
    parser_dropper_list_drops.add_argument(
        "-c",
        "--dropper-contract-id",
        type=str,
        required=True,
        help="Dropper contract id",
    )
    parser_dropper_list_drops.set_defaults(func=dropper_list_drops_handler)

    parser_dropper_delete_drop = subparsers_dropper.add_parser(
        "delete-drop", description="Delete dropper drop"
    )
    parser_dropper_delete_drop.add_argument(
        "-d",
        "--dropper-claim-id",
        type=str,
        required=True,
        help="Drop id in database",
    )
    parser_dropper_delete_drop.set_defaults(func=dropper_delete_drop_handler)

    parser_dropper_add_claimants = subparsers_dropper.add_parser(
        "add-claimants", description="Add claimants to drop"
    )
    parser_dropper_add_claimants.add_argument(
        "-c",
        "--dropper-claim-id",
        type=str,
        required=True,
        help="Id of particular claim",
    )
    parser_dropper_add_claimants.add_argument(
        "-f",
        "--claimants-file",
        type=str,
        required=True,
        help="Csv of claimants addresses",
    )
    parser_dropper_add_claimants.set_defaults(func=add_claimants_handler)

    parser_dropper_delete_claimants = subparsers_dropper.add_parser(
        "delete-claimants", description="Delete claimants from drop"
    )
    parser_dropper_delete_claimants.add_argument(
        "-c",
        "--dropper-claim-id",
        type=str,
        required=True,
        help="Id of particular claim",
    )
    parser_dropper_delete_claimants.add_argument(
        "-f",
        "--claimants-file",
        type=str,
        required=True,
        help="Csv of claimants addresses",
    )
    parser_dropper_delete_claimants.set_defaults(func=delete_claimants_handler)

    parser_dropper_list_claimants = subparsers_dropper.add_parser(
        "list-claimants", description="List claimants of drop"
    )
    parser_dropper_list_claimants.add_argument(
        "-c", "--dropper-claim-id", type=str, required=True, help="Dropper claim id"
    )
    parser_dropper_list_claimants.set_defaults(func=list_claimants_handler)

    parser_dropper_claimant_signature_refetch = subparsers_dropper.add_parser(
        "signature-refetch", description="Refetch signature for claimant"
    )
    parser_dropper_claimant_signature_refetch.add_argument(
        "--dropper-claim-id", type=str, required=True
    )

    parser_dropper_claimant_signature_refetch.set_defaults(
        func=claimant_signature_refetch_handler
    )

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
