from inspect import trace
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

        cls.admin_token_pool_id = cls._create_terminus_pool()

        cls.terminus.set_pool_controller(cls.admin_token_pool_id)

        cls.lootbox = Lootbox.Lootbox(None)
        cls.lootbox.deploy(
            cls.terminus.address, cls.admin_token_pool_id, {"from": accounts[0]}
        )

    def _create_terminus_pool(
        self, capacity=10 ** 18, transferable=True, burnable=True
    ) -> int:
        self.terminus.create_pool_v1(
            capacity,
            transferable,
            burnable,
            {"from": accounts[0]},
        )

        return self.terminus.total_pools()

    def _open_lootbox(self, account, lootboxId, count=None):
        """
        Open lootboxes with the given lootboxId and count.
        If count is None, open all available lootboxes.
        """
        lootbox_items_count = self.lootbox.lootbox_item_count(lootboxId)
        lootbox_terminus_pool_id = self.lootbox.terminus_pool_idby_lootbox_id(lootboxId)

        if count is None:
            count = self.terminus.balance_of(account.address, lootbox_terminus_pool_id)

        for i in range(lootbox_items_count):
            (
                reward_type,
                token_address,
                token_id,
                token_amount,
            ) = self.lootbox.get_lootbox_item_by_index(lootboxId, i)

            claimer_lootbox_balance_before = self.terminus.balance_of(
                account.address, lootbox_terminus_pool_id
            )

            if reward_type == 20:
                mockErc20 = MockErc20.MockErc20(token_address)

                contract_balance_before = mockErc20.balance_of(self.lootbox.address)
                claimer_balance_before = mockErc20.balance_of(account.address)

                self.lootbox.open_lootbox(lootboxId, count, {"from": account})

                contract_balance_after = mockErc20.balance_of(self.lootbox.address)
                claimer_balance_after = mockErc20.balance_of(account.address)

                self.assertEqual(
                    contract_balance_before - contract_balance_after,
                    token_amount * count,
                )
                self.assertEqual(
                    claimer_balance_after - claimer_balance_before,
                    token_amount * count,
                )
            elif reward_type == 1155:
                raise NotImplementedError
            else:
                raise ValueError(f"Unknown reward type: {reward_type}")

            self.assertEqual(
                claimer_lootbox_balance_before
                - self.terminus.balance_of(account.address, lootbox_terminus_pool_id),
                count,
            )


class LootboxBaseTest(LootboxTestCase):
    def test_lootbox_create_with_single_item(self):

        lootboxes_count_0 = self.lootbox.total_lootbox_count()

        self.lootbox.create_lootbox(
            [
                lootbox_item_to_tuple(
                    reward_type=20,
                    token_address=self.erc20_contracts[1].address,
                    token_id=0,
                    token_amount=10 * 10 ** 18,
                )
            ],
            {"from": accounts[0]},
        )

        self.erc20_contracts[1].mint(
            self.lootbox.address, 100 * 10 ** 18, {"from": accounts[0]}
        )

        lootboxes_count_1 = self.lootbox.total_lootbox_count()
        created_lootbox_id = self.lootbox.total_lootbox_count() - 1

        self.assertEqual(lootboxes_count_1, lootboxes_count_0 + 1)

        self.assertEqual(self.lootbox.lootbox_item_count(created_lootbox_id), 1)

        self.assertEqual(
            self.lootbox.get_lootbox_item_by_index(created_lootbox_id, 0),
            (20, self.erc20_contracts[0].address, 0, 10 * 10 ** 18),
        )

        lootbox_id = self.lootbox.total_lootbox_count() - 1
        self.lootbox.batch_mint_lootboxes(
            lootbox_id, [accounts[1].address], [1], {"from": accounts[0]}
        )

        self._open_lootbox(accounts[1], created_lootbox_id, 1)

    def test_lootbox_create_with_multiple_items(self):
        pool_ids = [self._create_terminus_pool() for _ in range(5)]


if __name__ == "__main__":
    unittest.main()
