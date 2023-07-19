from enum import Enum
import unittest

from brownie import accounts
from brownie.exceptions import VirtualMachineError

from .core import lootbox_item_to_tuple
from .test_lootbox import LootboxTestCase, LootboxTypes


class RandomLootboxTest(LootboxTestCase):
    def test_random_lootbox_creation_with_weight_zero_fails(self):
        new_lootbox = [
            lootbox_item_to_tuple(
                reward_type=20,
                token_address=self.erc20_contracts[1].address,
                token_id=0,
                token_amount=1 * 10**18,
                weight=4,
            ),
            lootbox_item_to_tuple(
                reward_type=20,
                token_address=self.erc20_contracts[1].address,
                token_id=0,
                token_amount=400 * 10**18,
                weight=0,
            ),
        ]

        with self.assertRaises(VirtualMachineError):
            self.lootbox.create_lootbox(
                new_lootbox, LootboxTypes.RANDOM_TYPE_1.value, {"from": accounts[0]}
            )

    def test_lootbox_item_add_with_zero_weight_fails(self):
        new_lootbox = [
            lootbox_item_to_tuple(
                reward_type=20,
                token_address=self.erc20_contracts[1].address,
                token_id=0,
                token_amount=400 * 10**18,
                weight=1,
            ),
        ]

        self.lootbox.create_lootbox(
            new_lootbox, LootboxTypes.RANDOM_TYPE_1.value, {"from": accounts[0]}
        )
        lootbox_id = self.lootbox.total_lootbox_count()
        with self.assertRaises(VirtualMachineError):
            self.lootbox.add_lootbox_item(
                lootbox_id,
                lootbox_item_to_tuple(
                    reward_type=20,
                    token_address=self.erc20_contracts[1].address,
                    token_id=0,
                    token_amount=400 * 10**18,
                    weight=0,
                ),
                {"from": accounts[0]},
            )

    def test_create_simple_random_lootbox(self):
        new_lootbox = [
            lootbox_item_to_tuple(
                reward_type=20,
                token_address=self.erc20_contracts[1].address,
                token_id=0,
                token_amount=400 * 10**18,
                weight=1,
            ),
            lootbox_item_to_tuple(
                reward_type=20,
                token_address=self.erc20_contracts[1].address,
                token_id=0,
                token_amount=1 * 10**18,
                weight=4,
            ),
        ]

        self.lootbox.create_lootbox(
            new_lootbox, LootboxTypes.RANDOM_TYPE_1.value, {"from": accounts[0]}
        )

        new_lootbox_id = self.lootbox.total_lootbox_count()

        self.lootbox.batch_mint_lootboxes_constant(
            new_lootbox_id,
            [accounts[1].address],
            3,
            {"from": accounts[0]},
        )

        contract_balance_0 = self.erc20_contracts[1].balance_of(self.lootbox.address)
        account_balance_0 = self.erc20_contracts[1].balance_of(accounts[1].address)

        self.lootbox.open_lootbox(
            new_lootbox_id,
            1,
            {"from": accounts[1]},
        )

        self.mock_vrf_oracle.fulfill_pending_requests(lambda: 0)

        self.lootbox.complete_random_lootbox_opening(
            {"from": accounts[1]},
        )

        contract_balance_1 = self.erc20_contracts[1].balance_of(self.lootbox.address)
        account_balance_1 = self.erc20_contracts[1].balance_of(accounts[1].address)

        self.assertEqual(contract_balance_0 - contract_balance_1, new_lootbox[0][3])
        self.assertEqual(account_balance_1 - account_balance_0, new_lootbox[0][3])

        self.lootbox.open_lootbox(
            new_lootbox_id,
            1,
            {"from": accounts[1]},
        )

        self.mock_vrf_oracle.fulfill_pending_requests(lambda: 1)

        self.lootbox.complete_random_lootbox_opening(
            {"from": accounts[1]},
        )

        contract_balance_2 = self.erc20_contracts[1].balance_of(self.lootbox.address)
        account_balance_2 = self.erc20_contracts[1].balance_of(accounts[1].address)

        self.assertEqual(contract_balance_1 - contract_balance_2, new_lootbox[1][3])
        self.assertEqual(account_balance_2 - account_balance_1, new_lootbox[1][3])

    def test_create_terminus_mintable_random_lootbox(self):
        new_lootbox = [
            lootbox_item_to_tuple(
                reward_type=1,
                token_address=self.terminus.address,
                token_id=self.reward_pool_id,
                token_amount=2,
                weight=1,
            ),
            lootbox_item_to_tuple(
                reward_type=1,
                token_address=self.terminus.address,
                token_id=self.reward_pool_id,
                token_amount=1,
                weight=4,
            ),
        ]

        self.lootbox.create_lootbox(
            new_lootbox, LootboxTypes.RANDOM_TYPE_1.value, {"from": accounts[0]}
        )

        new_lootbox_id = self.lootbox.total_lootbox_count()

        self.lootbox.batch_mint_lootboxes_constant(
            new_lootbox_id,
            [accounts[1].address],
            3,
            {"from": accounts[0]},
        )

        account_balance_0 = self.terminus.balance_of(
            accounts[1].address, self.reward_pool_id
        )

        self.lootbox.open_lootbox(
            new_lootbox_id,
            1,
            {"from": accounts[1]},
        )

        self.mock_vrf_oracle.fulfill_pending_requests(lambda: 0)

        self.lootbox.complete_random_lootbox_opening(
            {"from": accounts[1]},
        )

        account_balance_1 = self.terminus.balance_of(
            accounts[1].address, self.reward_pool_id
        )

        self.assertEqual(account_balance_1 - account_balance_0, new_lootbox[0][3])

        self.lootbox.open_lootbox(
            new_lootbox_id,
            1,
            {"from": accounts[1]},
        )

        self.mock_vrf_oracle.fulfill_pending_requests(lambda: 1)

        self.lootbox.complete_random_lootbox_opening(
            {"from": accounts[1]},
        )

        account_balance_2 = self.terminus.balance_of(
            accounts[1].address, self.reward_pool_id
        )

        self.assertEqual(account_balance_2 - account_balance_1, new_lootbox[1][3])

    def test_complex_random_lootbox(self):
        weigths = [1, 2, 3, 5, 5, 2, 1, 8, 9, 10]

        token_amounts = [weight * 10**18 for weight in weigths]
        new_lootbox = [
            lootbox_item_to_tuple(
                reward_type=20,
                token_address=self.erc20_contracts[1].address,
                token_id=0,
                token_amount=token_amount,
                weight=weight,
            )
            for token_amount, weight in zip(token_amounts, weigths)
        ]

        self.lootbox.create_lootbox(
            new_lootbox, LootboxTypes.RANDOM_TYPE_1.value, {"from": accounts[0]}
        )
        new_lootbox_id = self.lootbox.total_lootbox_count()
        self.lootbox.batch_mint_lootboxes_constant(
            new_lootbox_id,
            [accounts[1].address],
            10,
            {"from": accounts[0]},
        )

        weigths_sum = sum(weigths)
        current_weight = weigths_sum * 2  # should be x: x%weights_sum == 0

        for token_amount, weight in zip(token_amounts, weigths):
            account_balance_before = self.erc20_contracts[1].balance_of(
                accounts[1].address
            )
            self.lootbox.open_lootbox(
                new_lootbox_id,
                1,
                {"from": accounts[1]},
            )

            self.mock_vrf_oracle.fulfill_pending_requests(lambda: current_weight)
            self.lootbox.complete_random_lootbox_opening(
                {"from": accounts[1]},
            )

            account_balance_after = self.erc20_contracts[1].balance_of(
                accounts[1].address
            )
            self.assertEqual(
                account_balance_after - account_balance_before,
                token_amount,
            )

            current_weight += weight
