import argparse
import logging

from . import actions
from . import data
from . import Lootbox, core, drop, MockErc20, Dropper

logger = logging.getLogger(__name__)


def signing_server_wakeup_handler(args: argparse.Namespace) -> None:
    try:
        run_instances = actions.wakeup_instances(
            run_confirmed=args.confirmed, dry_run=args.dry_run
        )
    except actions.AWSRunInstancesFail:
        return
    except Exception as err:
        logger.error(f"Unhandled /wakeup exception: {err}")
        return

    print(data.WakeupResponse(instances=run_instances).json())


def signing_server_sleep_handler(args: argparse.Namespace) -> None:
    try:
        terminated_instances = actions.sleep_instances(
            signing_instances=[args.instance],
            termination_confirmed=args.confirmed,
            dry_run=args.dry_run,
        )
    except actions.AWSDescribeInstancesFail:
        return
    except actions.SigningInstancesNotFound:
        return
    except actions.SigningInstancesTerminationLimitExceeded:
        return
    except actions.AWSTerminateInstancesFail:
        return
    except Exception as err:
        logger.error(f"Unhandled /sleep exception: {err}")
        return

    print(data.SleepResponse(instances=terminated_instances).json())


def main():
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

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
