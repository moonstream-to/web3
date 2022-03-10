import unittest

from brownie import accounts, network
from . import Lootbox, MockTerminus, MockErc20


class LootboxTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            network.connect()
        except:
            pass

        cls.terminus = MockTerminus.MockTerminus()
        cls.terminus.deploy({"from": accounts[0]})

        cls.erc20_contracts = [MockErc20.MockErc20() for _ in range(5)]
        for contract in cls.erc20_contracts:
            contract.deploy({"from": accounts[0]})

        cls.erc20_contracts[0].mint(accounts[0], 100 * 10 ** 18)

        cls.terminus.set_payment_token(cls.mnstr.address, {"from": accounts[0]})
        cls.terminus.set_pool_base_price(1, {"from": accounts[0]})

        cls.erc20_contracts[0].approve(
            cls.terminus.address, 100 * 10 ** 18, {"from": accounts[0]}
        )

        cls.terminus.create_pool_v1(
            10,
            True,
            True,
            {"from": accounts[0]},
        )

        cls.admin_token_pool_id = 1

        cls.lootbox = Lootbox.Lootbox()
        cls.lootbox.deploy(
            cls.terminus.address, cls.admin_token_pool_id, {"from": accounts[0]}
        )
