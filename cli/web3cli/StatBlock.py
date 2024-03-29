# Code generated by moonworm : https://github.com/moonstream-to/moonworm
# Moonworm version : 0.7.1

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from brownie import Contract, network, project
from brownie.network.contract import ContractContainer
from eth_typing.evm import ChecksumAddress


PROJECT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUILD_DIRECTORY = os.path.join(PROJECT_DIRECTORY, "build", "contracts")


def boolean_argument_type(raw_value: str) -> bool:
    TRUE_VALUES = ["1", "t", "y", "true", "yes"]
    FALSE_VALUES = ["0", "f", "n", "false", "no"]

    if raw_value.lower() in TRUE_VALUES:
        return True
    elif raw_value.lower() in FALSE_VALUES:
        return False

    raise ValueError(
        f"Invalid boolean argument: {raw_value}. Value must be one of: {','.join(TRUE_VALUES + FALSE_VALUES)}"
    )


def bytes_argument_type(raw_value: str) -> str:
    return raw_value


def get_abi_json(abi_name: str) -> List[Dict[str, Any]]:
    abi_full_path = os.path.join(BUILD_DIRECTORY, f"{abi_name}.json")
    if not os.path.isfile(abi_full_path):
        raise IOError(
            f"File does not exist: {abi_full_path}. Maybe you have to compile the smart contracts?"
        )

    with open(abi_full_path, "r") as ifp:
        build = json.load(ifp)

    abi_json = build.get("abi")
    if abi_json is None:
        raise ValueError(f"Could not find ABI definition in: {abi_full_path}")

    return abi_json


def contract_from_build(abi_name: str) -> ContractContainer:
    # This is workaround because brownie currently doesn't support loading the same project multiple
    # times. This causes problems when using multiple contracts from the same project in the same
    # python project.
    PROJECT = project.main.Project("moonworm", Path(PROJECT_DIRECTORY))

    abi_full_path = os.path.join(BUILD_DIRECTORY, f"{abi_name}.json")
    if not os.path.isfile(abi_full_path):
        raise IOError(
            f"File does not exist: {abi_full_path}. Maybe you have to compile the smart contracts?"
        )

    with open(abi_full_path, "r") as ifp:
        build = json.load(ifp)

    return ContractContainer(PROJECT, build)


class StatBlock:
    def __init__(self, contract_address: Optional[ChecksumAddress]):
        self.contract_name = "StatBlock"
        self.address = contract_address
        self.contract = None
        self.abi = get_abi_json("StatBlock")
        if self.address is not None:
            self.contract: Optional[Contract] = Contract.from_abi(
                self.contract_name, self.address, self.abi
            )

    def deploy(
        self,
        admin_terminus_address: ChecksumAddress,
        admin_terminus_pool_id: int,
        transaction_config,
    ):
        contract_class = contract_from_build(self.contract_name)
        deployed_contract = contract_class.deploy(
            admin_terminus_address, admin_terminus_pool_id, transaction_config
        )
        self.address = deployed_contract.address
        self.contract = deployed_contract
        return deployed_contract.tx

    def assert_contract_is_instantiated(self) -> None:
        if self.contract is None:
            raise Exception("contract has not been instantiated")

    def verify_contract(self):
        self.assert_contract_is_instantiated()
        contract_class = contract_from_build(self.contract_name)
        contract_class.publish_source(self.contract)

    def num_stats(self, block_number: Optional[Union[str, int]] = "latest") -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.NumStats.call(block_identifier=block_number)

    def admin_terminus_info(
        self, block_number: Optional[Union[str, int]] = "latest"
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.adminTerminusInfo.call(block_identifier=block_number)

    def assign_stats(
        self,
        token_address: ChecksumAddress,
        token_id: int,
        stat_i_ds: List,
        values: List,
        transaction_config,
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.assignStats(
            token_address, token_id, stat_i_ds, values, transaction_config
        )

    def batch_assign_stats(
        self,
        token_addresses: List,
        token_i_ds: List,
        stat_i_ds: Any,
        values: Any,
        transaction_config,
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.batchAssignStats(
            token_addresses, token_i_ds, stat_i_ds, values, transaction_config
        )

    def batch_get_stats(
        self,
        token_addresses: List,
        token_i_ds: List,
        stat_i_ds: List,
        block_number: Optional[Union[str, int]] = "latest",
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.batchGetStats.call(
            token_addresses, token_i_ds, stat_i_ds, block_identifier=block_number
        )

    def create_stat(self, descriptor: str, transaction_config) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.createStat(descriptor, transaction_config)

    def describe_stat(
        self, stat_id: int, block_number: Optional[Union[str, int]] = "latest"
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.describeStat.call(stat_id, block_identifier=block_number)

    def get_stats(
        self,
        token_address: ChecksumAddress,
        token_id: int,
        stat_i_ds: List,
        block_number: Optional[Union[str, int]] = "latest",
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.getStats.call(
            token_address, token_id, stat_i_ds, block_identifier=block_number
        )

    def is_administrator(
        self,
        account: ChecksumAddress,
        block_number: Optional[Union[str, int]] = "latest",
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.isAdministrator.call(
            account, block_identifier=block_number
        )

    def set_stat_descriptor(
        self, stat_id: int, descriptor: str, transaction_config
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.setStatDescriptor(stat_id, descriptor, transaction_config)

    def stat_block_version(
        self, block_number: Optional[Union[str, int]] = "latest"
    ) -> Any:
        self.assert_contract_is_instantiated()
        return self.contract.statBlockVersion.call(block_identifier=block_number)


def get_transaction_config(args: argparse.Namespace) -> Dict[str, Any]:
    signer = network.accounts.load(args.sender, args.password)
    transaction_config: Dict[str, Any] = {"from": signer}
    if args.gas_price is not None:
        transaction_config["gas_price"] = args.gas_price
    if args.max_fee_per_gas is not None:
        transaction_config["max_fee"] = args.max_fee_per_gas
    if args.max_priority_fee_per_gas is not None:
        transaction_config["priority_fee"] = args.max_priority_fee_per_gas
    if args.confirmations is not None:
        transaction_config["required_confs"] = args.confirmations
    if args.nonce is not None:
        transaction_config["nonce"] = args.nonce
    return transaction_config


def add_default_arguments(parser: argparse.ArgumentParser, transact: bool) -> None:
    parser.add_argument(
        "--network", required=True, help="Name of brownie network to connect to"
    )
    parser.add_argument(
        "--address", required=False, help="Address of deployed contract to connect to"
    )
    if not transact:
        parser.add_argument(
            "--block-number",
            required=False,
            type=int,
            help="Call at the given block number, defaults to latest",
        )
        return
    parser.add_argument(
        "--sender", required=True, help="Path to keystore file for transaction sender"
    )
    parser.add_argument(
        "--password",
        required=False,
        help="Password to keystore file (if you do not provide it, you will be prompted for it)",
    )
    parser.add_argument(
        "--gas-price", default=None, help="Gas price at which to submit transaction"
    )
    parser.add_argument(
        "--max-fee-per-gas",
        default=None,
        help="Max fee per gas for EIP1559 transactions",
    )
    parser.add_argument(
        "--max-priority-fee-per-gas",
        default=None,
        help="Max priority fee per gas for EIP1559 transactions",
    )
    parser.add_argument(
        "--confirmations",
        type=int,
        default=None,
        help="Number of confirmations to await before considering a transaction completed",
    )
    parser.add_argument(
        "--nonce", type=int, default=None, help="Nonce for the transaction (optional)"
    )
    parser.add_argument(
        "--value", default=None, help="Value of the transaction in wei(optional)"
    )
    parser.add_argument("--verbose", action="store_true", help="Print verbose output")


def handle_deploy(args: argparse.Namespace) -> None:
    network.connect(args.network)
    transaction_config = get_transaction_config(args)
    contract = StatBlock(None)
    result = contract.deploy(
        admin_terminus_address=args.admin_terminus_address,
        admin_terminus_pool_id=args.admin_terminus_pool_id,
        transaction_config=transaction_config,
    )
    print(result)
    if args.verbose:
        print(result.info())


def handle_verify_contract(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = StatBlock(args.address)
    result = contract.verify_contract()
    print(result)


def handle_num_stats(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = StatBlock(args.address)
    result = contract.num_stats(block_number=args.block_number)
    print(result)


def handle_admin_terminus_info(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = StatBlock(args.address)
    result = contract.admin_terminus_info(block_number=args.block_number)
    print(result)


def handle_assign_stats(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = StatBlock(args.address)
    transaction_config = get_transaction_config(args)
    result = contract.assign_stats(
        token_address=args.token_address,
        token_id=args.token_id,
        stat_i_ds=args.stat_i_ds,
        values=args.values,
        transaction_config=transaction_config,
    )
    print(result)
    if args.verbose:
        print(result.info())


def handle_batch_assign_stats(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = StatBlock(args.address)
    transaction_config = get_transaction_config(args)
    result = contract.batch_assign_stats(
        token_addresses=args.token_addresses,
        token_i_ds=args.token_i_ds,
        stat_i_ds=args.stat_i_ds,
        values=args.values,
        transaction_config=transaction_config,
    )
    print(result)
    if args.verbose:
        print(result.info())


def handle_batch_get_stats(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = StatBlock(args.address)
    result = contract.batch_get_stats(
        token_addresses=args.token_addresses,
        token_i_ds=args.token_i_ds,
        stat_i_ds=args.stat_i_ds,
        block_number=args.block_number,
    )
    print(result)


def handle_create_stat(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = StatBlock(args.address)
    transaction_config = get_transaction_config(args)
    result = contract.create_stat(
        descriptor=args.descriptor, transaction_config=transaction_config
    )
    print(result)
    if args.verbose:
        print(result.info())


def handle_describe_stat(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = StatBlock(args.address)
    result = contract.describe_stat(
        stat_id=args.stat_id, block_number=args.block_number
    )
    print(result)


def handle_get_stats(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = StatBlock(args.address)
    result = contract.get_stats(
        token_address=args.token_address,
        token_id=args.token_id,
        stat_i_ds=args.stat_i_ds,
        block_number=args.block_number,
    )
    print(result)


def handle_is_administrator(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = StatBlock(args.address)
    result = contract.is_administrator(
        account=args.account, block_number=args.block_number
    )
    print(result)


def handle_set_stat_descriptor(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = StatBlock(args.address)
    transaction_config = get_transaction_config(args)
    result = contract.set_stat_descriptor(
        stat_id=args.stat_id,
        descriptor=args.descriptor,
        transaction_config=transaction_config,
    )
    print(result)
    if args.verbose:
        print(result.info())


def handle_stat_block_version(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = StatBlock(args.address)
    result = contract.stat_block_version(block_number=args.block_number)
    print(result)


def generate_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI for StatBlock")
    parser.set_defaults(func=lambda _: parser.print_help())
    subcommands = parser.add_subparsers()

    deploy_parser = subcommands.add_parser("deploy")
    add_default_arguments(deploy_parser, True)
    deploy_parser.add_argument(
        "--admin-terminus-address", required=True, help="Type: address"
    )
    deploy_parser.add_argument(
        "--admin-terminus-pool-id", required=True, help="Type: uint256", type=int
    )
    deploy_parser.set_defaults(func=handle_deploy)

    verify_contract_parser = subcommands.add_parser("verify-contract")
    add_default_arguments(verify_contract_parser, False)
    verify_contract_parser.set_defaults(func=handle_verify_contract)

    num_stats_parser = subcommands.add_parser("num-stats")
    add_default_arguments(num_stats_parser, False)
    num_stats_parser.set_defaults(func=handle_num_stats)

    admin_terminus_info_parser = subcommands.add_parser("admin-terminus-info")
    add_default_arguments(admin_terminus_info_parser, False)
    admin_terminus_info_parser.set_defaults(func=handle_admin_terminus_info)

    assign_stats_parser = subcommands.add_parser("assign-stats")
    add_default_arguments(assign_stats_parser, True)
    assign_stats_parser.add_argument(
        "--token-address", required=True, help="Type: address"
    )
    assign_stats_parser.add_argument(
        "--token-id", required=True, help="Type: uint256", type=int
    )
    assign_stats_parser.add_argument(
        "--stat-i-ds", required=True, help="Type: uint256[]", nargs="+"
    )
    assign_stats_parser.add_argument(
        "--values", required=True, help="Type: uint256[]", nargs="+"
    )
    assign_stats_parser.set_defaults(func=handle_assign_stats)

    batch_assign_stats_parser = subcommands.add_parser("batch-assign-stats")
    add_default_arguments(batch_assign_stats_parser, True)
    batch_assign_stats_parser.add_argument(
        "--token-addresses", required=True, help="Type: address[]", nargs="+"
    )
    batch_assign_stats_parser.add_argument(
        "--token-i-ds", required=True, help="Type: uint256[]", nargs="+"
    )
    batch_assign_stats_parser.add_argument(
        "--stat-i-ds", required=True, help="Type: uint256[][]", type=eval
    )
    batch_assign_stats_parser.add_argument(
        "--values", required=True, help="Type: uint256[][]", type=eval
    )
    batch_assign_stats_parser.set_defaults(func=handle_batch_assign_stats)

    batch_get_stats_parser = subcommands.add_parser("batch-get-stats")
    add_default_arguments(batch_get_stats_parser, False)
    batch_get_stats_parser.add_argument(
        "--token-addresses", required=True, help="Type: address[]", nargs="+"
    )
    batch_get_stats_parser.add_argument(
        "--token-i-ds", required=True, help="Type: uint256[]", nargs="+"
    )
    batch_get_stats_parser.add_argument(
        "--stat-i-ds", required=True, help="Type: uint256[]", nargs="+"
    )
    batch_get_stats_parser.set_defaults(func=handle_batch_get_stats)

    create_stat_parser = subcommands.add_parser("create-stat")
    add_default_arguments(create_stat_parser, True)
    create_stat_parser.add_argument(
        "--descriptor", required=True, help="Type: string", type=str
    )
    create_stat_parser.set_defaults(func=handle_create_stat)

    describe_stat_parser = subcommands.add_parser("describe-stat")
    add_default_arguments(describe_stat_parser, False)
    describe_stat_parser.add_argument(
        "--stat-id", required=True, help="Type: uint256", type=int
    )
    describe_stat_parser.set_defaults(func=handle_describe_stat)

    get_stats_parser = subcommands.add_parser("get-stats")
    add_default_arguments(get_stats_parser, False)
    get_stats_parser.add_argument(
        "--token-address", required=True, help="Type: address"
    )
    get_stats_parser.add_argument(
        "--token-id", required=True, help="Type: uint256", type=int
    )
    get_stats_parser.add_argument(
        "--stat-i-ds", required=True, help="Type: uint256[]", nargs="+"
    )
    get_stats_parser.set_defaults(func=handle_get_stats)

    is_administrator_parser = subcommands.add_parser("is-administrator")
    add_default_arguments(is_administrator_parser, False)
    is_administrator_parser.add_argument(
        "--account", required=True, help="Type: address"
    )
    is_administrator_parser.set_defaults(func=handle_is_administrator)

    set_stat_descriptor_parser = subcommands.add_parser("set-stat-descriptor")
    add_default_arguments(set_stat_descriptor_parser, True)
    set_stat_descriptor_parser.add_argument(
        "--stat-id", required=True, help="Type: uint256", type=int
    )
    set_stat_descriptor_parser.add_argument(
        "--descriptor", required=True, help="Type: string", type=str
    )
    set_stat_descriptor_parser.set_defaults(func=handle_set_stat_descriptor)

    stat_block_version_parser = subcommands.add_parser("stat-block-version")
    add_default_arguments(stat_block_version_parser, False)
    stat_block_version_parser.set_defaults(func=handle_stat_block_version)

    return parser


def main() -> None:
    parser = generate_cli()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
