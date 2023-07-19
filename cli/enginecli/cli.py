import argparse
import logging

from enginecli.ITerminus import ITerminus

from . import (
    core,
    flows,
    drop,
    DropperFacet,
    Dropper,
    Lootbox,
    MockErc20,
    MockERC721,
    ITerminus,
    setup_drop,
    CraftingFacet,
    GOFPFacet,
    InventoryFacet,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:

    parser = argparse.ArgumentParser(
        description="dao: The command line interface to Moonstream DAO"
    )
    parser.set_defaults(func=lambda _: parser.print_help())
    subparsers = parser.add_subparsers()

    core_parser = core.generate_cli()
    subparsers.add_parser("core", parents=[core_parser], add_help=False)

    flows_parser = flows.generate_cli()
    subparsers.add_parser("flows", parents=[flows_parser], add_help=False)

    dropper_parser = Dropper.generate_cli()
    subparsers.add_parser("dropper-v1", parents=[dropper_parser], add_help=False)

    dropper_facet_parser = DropperFacet.generate_cli()
    subparsers.add_parser("dropper", parents=[dropper_facet_parser], add_help=False)

    lootbox_parser = Lootbox.generate_cli()
    subparsers.add_parser("lootbox", parents=[lootbox_parser], add_help=False)

    erc20_parser = MockErc20.generate_cli()
    subparsers.add_parser("erc20", parents=[erc20_parser], add_help=False)

    erc721_parser = MockERC721.generate_cli()
    subparsers.add_parser("erc721", parents=[erc721_parser], add_help=False)

    drop_parser = drop.generate_cli()
    subparsers.add_parser("drop", parents=[drop_parser], add_help=False)

    terminus_parser = ITerminus.generate_cli()
    subparsers.add_parser("terminus", parents=[terminus_parser], add_help=False)

    crafting_parser = CraftingFacet.generate_cli()
    subparsers.add_parser("crafting", parents=[crafting_parser], add_help=False)

    gofp_parser = GOFPFacet.generate_cli()
    subparsers.add_parser("gofp", parents=[gofp_parser], add_help=False)

    setup_drop_parser = setup_drop.generate_cli()
    subparsers.add_parser("setup-drop", parents=[setup_drop_parser], add_help=False)

    inventory_parser = InventoryFacet.generate_cli()
    subparsers.add_parser("inventory", parents=[inventory_parser], add_help=False)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
