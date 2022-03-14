import unittest

from brownie import accounts, network
from . import Lootbox, MockTerminus, MockErc20
from .core import lootbox_item_to_tuple


class LootboxTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            network.connect()
        except:
            pass

        cls.terminus = MockTerminus.MockTerminus(None)
        cls.terminus.deploy({"from": accounts[0]})

        cls.erc20_contracts = [MockErc20.MockErc20(None) for _ in range(5)]
        for contract in cls.erc20_contracts:
            contract.deploy({"from": accounts[0]})

        cls.erc20_contracts[0].mint(accounts[0], 100 * 10 ** 18, {"from": accounts[0]})

        cls.terminus.set_payment_token(
            cls.erc20_contracts[0].address, {"from": accounts[0]}
        )
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

        cls.terminus.mint(accounts[0].address, 1, 10 ** 18, "", {"from": accounts[0]})

        cls.admin_token_pool_id = 1

        cls.lootbox = Lootbox.Lootbox(None)
        cls.lootbox.deploy(
            cls.terminus.address, cls.admin_token_pool_id, {"from": accounts[0]}
        )


class LootboxBaseTest(LootboxTestCase):
    def test_lootbox_create(self):

        self.terminus.create_pool_v1(
            1000,
            True,
            True,
            {"from": accounts[0]},
        )

        pool_id = self.terminus.total_pools()

        self.lootbox.create_lootbox(
            pool_id,
            [
                lootbox_item_to_tuple(
                    20, self.erc20_contracts[0].address, 0, 10 * 10 ** 18
                )
            ],
            {"from": accounts[0]},
        )


if __name__ == "__main__":
    unittest.main()
