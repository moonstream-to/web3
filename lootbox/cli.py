import argparse


from . import Lootbox, core, drop, MockErc20, Dropper


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

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
