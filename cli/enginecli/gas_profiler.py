import atexit
from typing import Optional
import brownie
from brownie.network import web3 as web3_client
from tabulate import tabulate
import json
import os

from .abi import project_abis, encode_function_signature

signatue_to_func = {}
gas_price: Optional[int] = None
eth_usd_price: Optional[int] = None


def gas_profile():
    # print(brownie.history.gas_profile)
    gas_usages_raw = {}
    for tx in brownie.history:
        if tx.status != 1:
            continue
        if tx.contract_name == "Diamond" and tx.fn_name == None:
            func_signature = tx.input[:10]
            tx.fn_name = signatue_to_func.get(func_signature, {"name": func_signature})[
                "name"
            ]
        function_name = f"{tx.contract_name}.{tx.fn_name}"
        gas_usages_raw.setdefault(function_name, []).append(tx.gas_used)

    gas_usages = {}
    table = []
    for function_name, gas_usage in gas_usages_raw.items():
        gas_usages[function_name] = {
            "avg": sum(gas_usage) / len(gas_usage),
            "max": max(gas_usage),
            "min": min(gas_usage),
            "count": len(gas_usage),
        }
        gas_usages[function_name]["fees"] = {}
        gas_usages[function_name]["fees"]["eth_fee_at_1_gwei"] = {
            "avg": gas_usages[function_name]["avg"] / 1_000_000_000,
            "max": gas_usages[function_name]["max"] / 1_000_000_000,
            "min": gas_usages[function_name]["min"] / 1_000_000_000,
        }
        table.append(
            [
                function_name,
                gas_usages[function_name]["min"],
                gas_usages[function_name]["max"],
                gas_usages[function_name]["avg"],
                gas_usages[function_name]["count"],
            ]
        )
        if gas_price and eth_usd_price:
            multiplier = gas_price
            gas_usages[function_name]["fees"]["eth_fee"] = {
                "gas_price": gas_price,
                "avg": gas_usages[function_name]["fees"]["eth_fee_at_1_gwei"]["avg"]
                * multiplier,
                "max": gas_usages[function_name]["fees"]["eth_fee_at_1_gwei"]["max"]
                * multiplier,
                "min": gas_usages[function_name]["fees"]["eth_fee_at_1_gwei"]["min"]
                * multiplier,
            }
            if eth_usd_price:
                multiplier = gas_price * eth_usd_price
                gas_usages[function_name]["fees"]["usd_fee"] = {
                    "gas_price": gas_price,
                    "eth_usd_price": eth_usd_price,
                    "avg": gas_usages[function_name]["fees"]["eth_fee_at_1_gwei"]["avg"]
                    * multiplier,
                    "max": gas_usages[function_name]["fees"]["eth_fee_at_1_gwei"]["max"]
                    * multiplier,
                    "min": gas_usages[function_name]["fees"]["eth_fee_at_1_gwei"]["min"]
                    * multiplier,
                }

    print(
        tabulate(
            table,
            headers=["Function", "Min", "Max", "Avg", "Count"],
            tablefmt="fancy_grid",
            floatfmt=".2f",
        )
    )

    with open("gas_usages.json", "w") as f:
        f.write(json.dumps(gas_usages, indent=4))
        print("gas usages saved to gas_usages.json")


if os.environ.get("GAS_PROFILE") is not None:
    print("gas profiling enabled")
    atexit.register(gas_profile)
    contract_abis = project_abis(".")

    gas_price = os.environ.get("GAS_PROFILE_GAS_PRICE")
    if gas_price is not None:
        gas_price = int(gas_price)
        print(f"gas price set to {gas_price}")
    eth_usd_price = os.environ.get("GAS_PROFILE_ETH_USD_PRICE")
    if eth_usd_price is not None:
        eth_usd_price = int(eth_usd_price)
        print(f"eth usd price set to {eth_usd_price}")

    for _, contract_abi in contract_abis.items():
        for abi_item in contract_abi:
            if abi_item["type"] == "function":
                signature = encode_function_signature(abi_item)
                signatue_to_func[signature] = abi_item
