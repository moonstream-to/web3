import unittest
from venv import create

from brownie import accounts, network
from brownie.exceptions import VirtualMachineError
from . import Lootbox, MockTerminus, MockErc20
from .core import lootbox_item_to_tuple, gogogo


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

        gogogo_result = gogogo(cls.terminus.address, {"from": accounts[0]})

        cls.erc20_contracts[0].approve(
            cls.terminus.address, 100 * 10 ** 18, {"from": accounts[0]}
        )
        cls.lootbox = Lootbox.Lootbox(gogogo_result["Lootbox"])
        cls.admin_token_pool_id = gogogo_result["adminTokenPoolId"]

        cls.terminus.set_controller(cls.lootbox.address, {"from": accounts[0]})

        for i in range(5):
            cls.erc20_contracts[i].mint(
                cls.lootbox.address,
                (100 ** 18) * (10 ** 18),
                {"from": accounts[0]},
            )

    def _create_terminus_pool(
        self, capacity=10 ** 18, transferable=True, burnable=True
    ) -> int:
        self.lootbox.surrender_terminus_control({"from": accounts[0]})
        self.terminus.create_pool_v1(
            capacity,
            transferable,
            burnable,
            {"from": accounts[0]},
        )
        self.terminus.set_controller(self.lootbox.address, {"from": accounts[0]})

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

            # TODO(yhtiyar) remove this shit. Currently it is done like this, cuz we don't have much time
            network.chain.snapshot()

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
                mockErc1155 = MockTerminus.MockTerminus(token_address)
                contract_balance_before = mockErc1155.balance_of(
                    self.lootbox.address, token_id
                )
                claimer_balance_before = mockErc1155.balance_of(
                    account.address, token_id
                )

                self.lootbox.open_lootbox(lootboxId, count, {"from": account})

                contract_balance_after = mockErc1155.balance_of(
                    self.lootbox.address, token_id
                )
                claimer_balance_after = mockErc1155.balance_of(
                    account.address, token_id
                )

                self.assertEqual(
                    contract_balance_before - contract_balance_after,
                    token_amount * count,
                )
                self.assertEqual(
                    claimer_balance_after - claimer_balance_before,
                    token_amount * count,
                )

            else:
                raise ValueError(f"Unknown reward type: {reward_type}")

            self.assertEqual(
                claimer_lootbox_balance_before
                - self.terminus.balance_of(account.address, lootbox_terminus_pool_id),
                count,
            )
            network.chain.revert()


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
        created_lootbox_id = self.lootbox.total_lootbox_count()

        self.assertEqual(lootboxes_count_1, lootboxes_count_0 + 1)

        self.assertEqual(self.lootbox.lootbox_item_count(created_lootbox_id), 1)

        self.assertEqual(
            self.lootbox.get_lootbox_item_by_index(created_lootbox_id, 0),
            (20, self.erc20_contracts[1].address, 0, 10 * 10 ** 18),
        )

        self.lootbox.set_lootbox_uri(created_lootbox_id, "lol", {"from": accounts[0]})
        self.assertEquals(self.lootbox.get_lootbox_uri(created_lootbox_id), "lol")

        self.lootbox.batch_mint_lootboxes(
            created_lootbox_id, [accounts[1].address], [1], {"from": accounts[0]}
        )

        self._open_lootbox(accounts[1], created_lootbox_id, 1)

    def test_mint_lootboxes(self):
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

        lootbox_id = self.lootbox.total_lootbox_count()

        self.lootbox.mint_lootbox(
            lootbox_id,
            accounts[1].address,
            5,
            "",
            {"from": accounts[0]},
        )

        balance = self.lootbox.get_lootbox_balance(lootbox_id, accounts[1].address)

        self.assertEqual(balance, 5)

    def test_batch_mint_lootboxes(self):

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

        lootbox_id = self.lootbox.total_lootbox_count()

        self.lootbox.batch_mint_lootboxes(
            lootbox_id,
            [accounts[1].address, accounts[2].address, accounts[3].address],
            [1, 2, 3],
            {"from": accounts[0]},
        )

        balances = (
            self.lootbox.get_lootbox_balance(lootbox_id, accounts[1].address),
            self.lootbox.get_lootbox_balance(lootbox_id, accounts[2].address),
            self.lootbox.get_lootbox_balance(lootbox_id, accounts[3].address),
        )

        self.assertEqual(balances, (1, 2, 3))

    def test_batch_mint_lootboxes_constant(self):
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

        lootbox_id = self.lootbox.total_lootbox_count()

        self.lootbox.batch_mint_lootboxes_constant(
            lootbox_id,
            [accounts[1].address, accounts[2].address, accounts[3].address],
            2,
            {"from": accounts[0]},
        )

        balances = (
            self.lootbox.get_lootbox_balance(lootbox_id, accounts[1].address),
            self.lootbox.get_lootbox_balance(lootbox_id, accounts[2].address),
            self.lootbox.get_lootbox_balance(lootbox_id, accounts[3].address),
        )

        self.assertEqual(balances, (2, 2, 2))

    def test_lootbox_create_with_multiple_items(self):

        erc20_rewards = [
            lootbox_item_to_tuple(
                reward_type=20,
                token_address=self.erc20_contracts[i].address,
                token_id=0,
                token_amount=i * 15 * 10 ** 18,
            )
            for i in range(3)
        ]

        erc1155_rewards_ids = [self._create_terminus_pool() for _ in range(3)]

        erc1155_rewards = [
            lootbox_item_to_tuple(
                reward_type=1155,
                token_address=self.terminus.address,
                token_id=i,
                token_amount=5,
            )
            for i in erc1155_rewards_ids
        ]

        for id in erc1155_rewards_ids:
            self.terminus.mint(
                self.lootbox.address, id, 50000, "", {"from": accounts[0]}
            )

        lootbox_items = erc20_rewards + erc1155_rewards

        lootbox_items = erc20_rewards

        self.lootbox.create_lootbox(lootbox_items, {"from": accounts[0]})
        lootbox_id = self.lootbox.total_lootbox_count()

        self.lootbox.batch_mint_lootboxes(
            lootbox_id,
            [accounts[1].address, accounts[2].address, accounts[3].address],
            [1, 2, 3],
            {"from": accounts[0]},
        )
        self.assertEqual(self.lootbox.get_lootbox_balance(lootbox_id, accounts[1]), 1)

        terminus_pool_id = self.lootbox.terminus_pool_idby_lootbox_id(lootbox_id)
        self.assertEqual(
            self.terminus.balance_of(accounts[1].address, terminus_pool_id), 1
        )

        # self.lootbox.open_lootbox(lootbox_id, 1, {"from": accounts[1]})
        self._open_lootbox(accounts[1], lootbox_id, 1)

        self._open_lootbox(accounts[2], lootbox_id, 1)
        self._open_lootbox(accounts[2], lootbox_id, 1)

        self._open_lootbox(accounts[3], lootbox_id, 3)
        # with self.assertRaises(Exception):
        #    self._open_lootbox(accounts[3], lootbox_id, 1)

    def test_add_and_remove_lootbox(self):
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

        lootbox_id = self.lootbox.total_lootbox_count()

        newLootboxItem = lootbox_item_to_tuple(
            reward_type=20,
            token_address=self.erc20_contracts[2].address,
            token_id=0,
            token_amount=10 * 10 ** 18,
        )

        self.lootbox.add_lootbox_item(lootbox_id, newLootboxItem, {"from": accounts[0]})

        self.assertEqual(self.lootbox.lootbox_item_count(lootbox_id), 2)
        self.assertEquals(
            self.lootbox.get_lootbox_item_by_index(lootbox_id, 1), newLootboxItem
        )

        self.lootbox.remove_lootbox_item(lootbox_id, 0, {"from": accounts[0]})

        self.assertEqual(self.lootbox.lootbox_item_count(lootbox_id), 1)
        self.assertEquals(
            self.lootbox.get_lootbox_item_by_index(lootbox_id, 0), newLootboxItem
        )

        self.lootbox.remove_lootbox_item(lootbox_id, 0, {"from": accounts[0]})

        self.assertEqual(self.lootbox.lootbox_item_count(lootbox_id), 0)

    def test_withdraw_erc20(self):
        token_amount = 43
        lootbox_balance_0 = self.erc20_contracts[0].balance_of(self.lootbox.address)
        account_balance_0 = self.erc20_contracts[0].balance_of(accounts[0].address)
        self.erc20_contracts[0].mint(
            self.lootbox.address, token_amount, {"from": accounts[0]}
        )
        lootbox_balance_1 = self.erc20_contracts[0].balance_of(self.lootbox.address)
        account_balance_1 = self.erc20_contracts[0].balance_of(accounts[0].address)
        self.assertEqual(lootbox_balance_1, lootbox_balance_0 + token_amount)
        self.assertEqual(account_balance_1, account_balance_0)
        self.lootbox.withdraw_erc20(
            self.erc20_contracts[0].address, token_amount, {"from": accounts[0]}
        )
        lootbox_balance_2 = self.erc20_contracts[0].balance_of(self.lootbox.address)
        account_balance_2 = self.erc20_contracts[0].balance_of(accounts[0].address)
        self.assertEqual(lootbox_balance_2, lootbox_balance_1 - token_amount)
        self.assertEqual(account_balance_2, account_balance_1 + token_amount)

    def test_withdraw_erc1155(self):
        token_amount = 53
        withdraw_amount = 47
        fresh_erc1155 = MockTerminus.MockTerminus(None)
        fresh_erc1155.deploy({"from": accounts[0]})
        fresh_erc1155.set_payment_token(
            self.erc20_contracts[0].address, {"from": accounts[0]}
        )

        fresh_erc1155.create_pool_v1(
            10 * token_amount, True, True, {"from": accounts[0]}
        )
        pool_id = fresh_erc1155.total_pools()
        lootbox_balance_0 = fresh_erc1155.balance_of(self.lootbox.address, pool_id)
        account_balance_0 = fresh_erc1155.balance_of(accounts[0].address, pool_id)
        fresh_erc1155.mint(
            self.lootbox.address, pool_id, token_amount, b"", {"from": accounts[0]}
        )
        lootbox_balance_1 = fresh_erc1155.balance_of(self.lootbox.address, pool_id)
        account_balance_1 = fresh_erc1155.balance_of(accounts[0].address, pool_id)
        self.assertEqual(lootbox_balance_1, lootbox_balance_0 + token_amount)
        self.assertEqual(account_balance_1, account_balance_0)
        self.lootbox.withdraw_erc1155(
            fresh_erc1155.address, pool_id, withdraw_amount, {"from": accounts[0]}
        )
        lootbox_balance_2 = fresh_erc1155.balance_of(self.lootbox.address, pool_id)
        account_balance_2 = fresh_erc1155.balance_of(accounts[0].address, pool_id)
        self.assertEqual(lootbox_balance_2, lootbox_balance_1 - withdraw_amount)
        self.assertEqual(account_balance_2, account_balance_1 + withdraw_amount)


class LootboxACLTests(LootboxTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.lootbox.grant_admin_role(accounts[1].address, {"from": accounts[0]})

    def test_nonadmin_cannot_create_lootbox(self):
        lootboxes_count_0 = self.lootbox.total_lootbox_count()
        with self.assertRaises(VirtualMachineError):
            self.lootbox.create_lootbox(
                [
                    lootbox_item_to_tuple(
                        reward_type=20,
                        token_address=self.erc20_contracts[1].address,
                        token_id=0,
                        token_amount=10 * 10 ** 18,
                    )
                ],
                {"from": accounts[2]},
            )
        lootboxes_count_1 = self.lootbox.total_lootbox_count()
        self.assertEqual(lootboxes_count_1, lootboxes_count_0)

    def test_admin_can_create_and_mint_working_lootbox(self):
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
            {"from": accounts[1]},
        )

        self.erc20_contracts[1].mint(
            self.lootbox.address, 100 * 10 ** 18, {"from": accounts[0]}
        )

        lootboxes_count_1 = self.lootbox.total_lootbox_count()
        created_lootbox_id = self.lootbox.total_lootbox_count()

        self.assertEqual(lootboxes_count_1, lootboxes_count_0 + 1)

        self.assertEqual(self.lootbox.lootbox_item_count(created_lootbox_id), 1)

        self.assertEqual(
            self.lootbox.get_lootbox_item_by_index(created_lootbox_id, 0),
            (20, self.erc20_contracts[1].address, 0, 10 * 10 ** 18),
        )

        self.lootbox.batch_mint_lootboxes(
            created_lootbox_id, [accounts[3].address], [1], {"from": accounts[1]}
        )

        recipient_erc20_balance_0 = self.erc20_contracts[1].balance_of(
            accounts[3].address
        )
        self.lootbox.open_lootbox(created_lootbox_id, 1, {"from": accounts[3]})
        recipient_erc20_balance_1 = self.erc20_contracts[1].balance_of(
            accounts[3].address
        )
        self.assertEqual(
            recipient_erc20_balance_1, recipient_erc20_balance_0 + (10 * (10 ** 18))
        )

    def test_nonadmin_cannot_mint_lootbox_created_by_admin(self):
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
            {"from": accounts[1]},
        )

        self.erc20_contracts[1].mint(
            self.lootbox.address, 100 * 10 ** 18, {"from": accounts[0]}
        )

        lootboxes_count_1 = self.lootbox.total_lootbox_count()
        created_lootbox_id = self.lootbox.total_lootbox_count()

        self.assertEqual(lootboxes_count_1, lootboxes_count_0 + 1)
        self.assertEqual(self.lootbox.lootbox_item_count(created_lootbox_id), 1)

        with self.assertRaises(VirtualMachineError):
            self.lootbox.batch_mint_lootboxes(
                created_lootbox_id, [accounts[3].address], [1], {"from": accounts[2]}
            )

    def test_admin_can_create_and_batch_mint_constant_working_lootbox(self):
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
            {"from": accounts[1]},
        )

        self.erc20_contracts[1].mint(
            self.lootbox.address, 100 * 10 ** 18, {"from": accounts[0]}
        )

        lootboxes_count_1 = self.lootbox.total_lootbox_count()
        created_lootbox_id = self.lootbox.total_lootbox_count()

        self.assertEqual(lootboxes_count_1, lootboxes_count_0 + 1)

        self.assertEqual(self.lootbox.lootbox_item_count(created_lootbox_id), 1)

        self.assertEqual(
            self.lootbox.get_lootbox_item_by_index(created_lootbox_id, 0),
            (20, self.erc20_contracts[1].address, 0, 10 * 10 ** 18),
        )

        self.lootbox.batch_mint_lootboxes_constant(
            created_lootbox_id, [accounts[3].address], 1, {"from": accounts[1]}
        )

        recipient_erc20_balance_0 = self.erc20_contracts[1].balance_of(
            accounts[3].address
        )
        self.lootbox.open_lootbox(created_lootbox_id, 1, {"from": accounts[3]})
        recipient_erc20_balance_1 = self.erc20_contracts[1].balance_of(
            accounts[3].address
        )
        self.assertEqual(
            recipient_erc20_balance_1, recipient_erc20_balance_0 + (10 * (10 ** 18))
        )

    def test_nonadmin_cannot_batch_mint_constant_lootbox_created_by_admin(self):
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
            {"from": accounts[1]},
        )

        self.erc20_contracts[1].mint(
            self.lootbox.address, 100 * 10 ** 18, {"from": accounts[0]}
        )

        lootboxes_count_1 = self.lootbox.total_lootbox_count()
        created_lootbox_id = self.lootbox.total_lootbox_count()

        self.assertEqual(lootboxes_count_1, lootboxes_count_0 + 1)
        self.assertEqual(self.lootbox.lootbox_item_count(created_lootbox_id), 1)

        with self.assertRaises(VirtualMachineError):
            self.lootbox.batch_mint_lootboxes_constant(
                created_lootbox_id, [accounts[3].address], 1, {"from": accounts[2]}
            )

    def test_admin_cannot_withdraw_erc20(self):
        token_amount = 43
        lootbox_balance_0 = self.erc20_contracts[0].balance_of(self.lootbox.address)
        account_balance_0 = self.erc20_contracts[0].balance_of(accounts[1].address)
        self.erc20_contracts[0].mint(
            self.lootbox.address, token_amount, {"from": accounts[0]}
        )
        lootbox_balance_1 = self.erc20_contracts[0].balance_of(self.lootbox.address)
        account_balance_1 = self.erc20_contracts[0].balance_of(accounts[1].address)
        self.assertEqual(lootbox_balance_1, lootbox_balance_0 + token_amount)
        self.assertEqual(account_balance_1, account_balance_0)
        with self.assertRaises(VirtualMachineError):
            self.lootbox.withdraw_erc20(
                self.erc20_contracts[0].address, token_amount, {"from": accounts[1]}
            )
        lootbox_balance_2 = self.erc20_contracts[0].balance_of(self.lootbox.address)
        account_balance_2 = self.erc20_contracts[0].balance_of(accounts[1].address)
        self.assertEqual(lootbox_balance_2, lootbox_balance_1)
        self.assertEqual(account_balance_2, account_balance_1)

    def test_admin_cannot_withdraw_erc1155(self):
        token_amount = 53
        withdraw_amount = 47
        fresh_erc1155 = MockTerminus.MockTerminus(None)
        fresh_erc1155.deploy({"from": accounts[1]})
        fresh_erc1155.set_payment_token(
            self.erc20_contracts[0].address, {"from": accounts[1]}
        )

        fresh_erc1155.create_pool_v1(
            10 * token_amount, True, True, {"from": accounts[1]}
        )
        pool_id = fresh_erc1155.total_pools()
        lootbox_balance_0 = fresh_erc1155.balance_of(self.lootbox.address, pool_id)
        account_balance_0 = fresh_erc1155.balance_of(accounts[1].address, pool_id)
        fresh_erc1155.mint(
            self.lootbox.address, pool_id, token_amount, b"", {"from": accounts[1]}
        )
        lootbox_balance_1 = fresh_erc1155.balance_of(self.lootbox.address, pool_id)
        account_balance_1 = fresh_erc1155.balance_of(accounts[1].address, pool_id)
        self.assertEqual(lootbox_balance_1, lootbox_balance_0 + token_amount)
        self.assertEqual(account_balance_1, account_balance_0)
        with self.assertRaises(VirtualMachineError):
            self.lootbox.withdraw_erc1155(
                fresh_erc1155.address, pool_id, withdraw_amount, {"from": accounts[1]}
            )
        lootbox_balance_2 = fresh_erc1155.balance_of(self.lootbox.address, pool_id)
        account_balance_2 = fresh_erc1155.balance_of(accounts[1].address, pool_id)
        self.assertEqual(lootbox_balance_2, lootbox_balance_1)
        self.assertEqual(account_balance_2, account_balance_1)

    def test_nonadmin_cannot_withdraw_erc20(self):
        token_amount = 43
        lootbox_balance_0 = self.erc20_contracts[0].balance_of(self.lootbox.address)
        account_balance_0 = self.erc20_contracts[0].balance_of(accounts[2].address)
        self.erc20_contracts[0].mint(
            self.lootbox.address, token_amount, {"from": accounts[0]}
        )
        lootbox_balance_1 = self.erc20_contracts[0].balance_of(self.lootbox.address)
        account_balance_1 = self.erc20_contracts[0].balance_of(accounts[2].address)
        self.assertEqual(lootbox_balance_1, lootbox_balance_0 + token_amount)
        self.assertEqual(account_balance_1, account_balance_0)
        with self.assertRaises(VirtualMachineError):
            self.lootbox.withdraw_erc20(
                self.erc20_contracts[0].address, token_amount, {"from": accounts[2]}
            )
        lootbox_balance_2 = self.erc20_contracts[0].balance_of(self.lootbox.address)
        account_balance_2 = self.erc20_contracts[0].balance_of(accounts[2].address)
        self.assertEqual(lootbox_balance_2, lootbox_balance_1)
        self.assertEqual(account_balance_2, account_balance_1)

    def test_nonadmin_cannot_withdraw_erc1155(self):
        token_amount = 53
        withdraw_amount = 47
        fresh_erc1155 = MockTerminus.MockTerminus(None)
        fresh_erc1155.deploy({"from": accounts[2]})
        fresh_erc1155.set_payment_token(
            self.erc20_contracts[0].address, {"from": accounts[2]}
        )

        fresh_erc1155.create_pool_v1(
            10 * token_amount, True, True, {"from": accounts[2]}
        )
        pool_id = fresh_erc1155.total_pools()
        lootbox_balance_0 = fresh_erc1155.balance_of(self.lootbox.address, pool_id)
        account_balance_0 = fresh_erc1155.balance_of(accounts[2].address, pool_id)
        fresh_erc1155.mint(
            self.lootbox.address, pool_id, token_amount, b"", {"from": accounts[2]}
        )
        lootbox_balance_1 = fresh_erc1155.balance_of(self.lootbox.address, pool_id)
        account_balance_1 = fresh_erc1155.balance_of(accounts[2].address, pool_id)
        self.assertEqual(lootbox_balance_1, lootbox_balance_0 + token_amount)
        self.assertEqual(account_balance_1, account_balance_0)
        with self.assertRaises(VirtualMachineError):
            self.lootbox.withdraw_erc1155(
                fresh_erc1155.address, pool_id, withdraw_amount, {"from": accounts[2]}
            )
        lootbox_balance_2 = fresh_erc1155.balance_of(self.lootbox.address, pool_id)
        account_balance_2 = fresh_erc1155.balance_of(accounts[2].address, pool_id)
        self.assertEqual(lootbox_balance_2, lootbox_balance_1)
        self.assertEqual(account_balance_2, account_balance_1)

    def test_owner_can_surrender_terminus_control(self):
        controller_0 = self.terminus.terminus_controller()
        self.assertEqual(controller_0, self.lootbox.address)

        self.lootbox.surrender_terminus_control({"from": accounts[0]})

        controller_1 = self.terminus.terminus_controller()
        self.assertEqual(controller_1, accounts[0].address)

        self.terminus.set_controller(self.lootbox.address, {"from": accounts[0]})
        controller_2 = self.terminus.terminus_controller()
        self.assertEqual(controller_2, self.lootbox.address)

    def test_admin_cannot_surrender_terminus_control(self):
        controller_0 = self.terminus.terminus_controller()
        self.assertEqual(controller_0, self.lootbox.address)

        with self.assertRaises(VirtualMachineError):
            self.lootbox.surrender_terminus_control({"from": accounts[1]})

        controller_1 = self.terminus.terminus_controller()
        self.assertEqual(controller_1, self.lootbox.address)

    def test_nonadmin_cannot_surrender_terminus_control(self):
        controller_0 = self.terminus.terminus_controller()
        self.assertEqual(controller_0, self.lootbox.address)

        with self.assertRaises(VirtualMachineError):
            self.lootbox.surrender_terminus_control({"from": accounts[2]})

        controller_1 = self.terminus.terminus_controller()
        self.assertEqual(controller_1, self.lootbox.address)

    def test_owner_can_surrender_terminus_pools(self):
        self.lootbox.create_lootbox(
            [
                lootbox_item_to_tuple(
                    reward_type=20,
                    token_address=self.erc20_contracts[-1].address,
                    token_id=0,
                    token_amount=1,
                ),
                lootbox_item_to_tuple(
                    reward_type=20,
                    token_address=self.erc20_contracts[-1].address,
                    token_id=0,
                    token_amount=2,
                ),
            ],
            {"from": accounts[0]},
        )
        last_pool_id = self.terminus.total_pools()
        pool_ids = [last_pool_id - 1, last_pool_id]

        for pool_id in pool_ids:
            controller_0 = self.terminus.terminus_pool_controller(pool_id)
            self.assertEqual(controller_0, self.lootbox.address)

        self.lootbox.surrender_terminus_pools(pool_ids, {"from": accounts[0]})

        for pool_id in pool_ids:
            controller_1 = self.terminus.terminus_pool_controller(pool_id)
            self.assertEqual(controller_1, accounts[0].address)

    def test_admin_cannot_surrender_terminus_pools(self):
        self.lootbox.create_lootbox(
            [
                lootbox_item_to_tuple(
                    reward_type=20,
                    token_address=self.erc20_contracts[-1].address,
                    token_id=0,
                    token_amount=1,
                )
            ],
            {"from": accounts[0]},
        )
        pool_id = self.terminus.total_pools()

        controller_0 = self.terminus.terminus_pool_controller(pool_id)
        self.assertEqual(controller_0, self.lootbox.address)

        with self.assertRaises(VirtualMachineError):
            self.lootbox.surrender_terminus_pools([pool_id], {"from": accounts[1]})

        controller_1 = self.terminus.terminus_pool_controller(pool_id)
        self.assertEqual(controller_1, self.lootbox.address)

    def test_nonadmin_cannot_surrender_terminus_pools(self):
        self.lootbox.create_lootbox(
            [
                lootbox_item_to_tuple(
                    reward_type=20,
                    token_address=self.erc20_contracts[-1].address,
                    token_id=0,
                    token_amount=1,
                )
            ],
            {"from": accounts[0]},
        )
        pool_id = self.terminus.total_pools()

        controller_0 = self.terminus.terminus_pool_controller(pool_id)
        self.assertEqual(controller_0, self.lootbox.address)

        with self.assertRaises(VirtualMachineError):
            self.lootbox.surrender_terminus_pools([pool_id], {"from": accounts[2]})

        controller_1 = self.terminus.terminus_pool_controller(pool_id)
        self.assertEqual(controller_1, self.lootbox.address)


if __name__ == "__main__":
    unittest.main()
