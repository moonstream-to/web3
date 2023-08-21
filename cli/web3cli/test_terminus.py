from typing import List
import unittest

from brownie import accounts, network
from brownie.exceptions import VirtualMachineError

from . import MockErc20, TerminusFacet
from .core import terminus_gogogo


class TerminusTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            network.connect()
        except:
            pass

        cls.deployment_info = terminus_gogogo({"from": accounts[0]})
        cls.terminus = TerminusFacet.TerminusFacet(
            cls.deployment_info["contracts"]["Diamond"]
        )

        cls.erc20 = MockErc20.MockErc20(None)
        cls.erc20.deploy("test", "test", {"from": accounts[0]})


class TestDeployment(TerminusTestCase):
    def test_deployment(self):
        controller = self.terminus.terminus_controller()
        self.assertEqual(controller, accounts[0].address)


class TestController(TerminusTestCase):
    def test_set_controller_fails_when_not_called_by_controller(self):
        with self.assertRaises(VirtualMachineError):
            self.terminus.set_controller(accounts[1].address, {"from": accounts[1]})

    def test_set_controller_fails_when_not_called_by_controller_even_if_they_change_to_existing_controller(
        self,
    ):
        with self.assertRaises(VirtualMachineError):
            self.terminus.set_controller(accounts[0].address, {"from": accounts[1]})

    def test_set_controller(self):
        self.assertEqual(self.terminus.terminus_controller(), accounts[0].address)
        self.terminus.set_controller(accounts[3].address, {"from": accounts[0]})
        self.assertEqual(self.terminus.terminus_controller(), accounts[3].address)
        self.terminus.set_controller(accounts[0].address, {"from": accounts[3]})
        self.assertEqual(self.terminus.terminus_controller(), accounts[0].address)


class TestContractURI(TerminusTestCase):
    def test_contract_uri(self):
        contract_uri = self.terminus.contract_uri()
        self.assertEqual(contract_uri, "")

        self.terminus.set_contract_uri("https://example.com", {"from": accounts[0]})

        contract_uri = self.terminus.contract_uri()
        self.assertEqual(contract_uri, "https://example.com")


class TestSimplePoolCreation(TerminusTestCase):
    def test_create_simple_pool(self):
        self.terminus.set_payment_token(self.erc20.address, {"from": accounts[0]})
        payment_token = self.terminus.payment_token()
        self.assertEqual(payment_token, self.erc20.address)

        self.terminus.set_pool_base_price(1000, {"from": accounts[0]})
        pool_base_price = self.terminus.pool_base_price()
        self.assertEqual(pool_base_price, 1000)

        self.terminus.set_controller(accounts[1].address, {"from": accounts[0]})

        self.erc20.mint(accounts[1], 1000, {"from": accounts[0]})
        initial_payer_balance = self.erc20.balance_of(accounts[1].address)
        initial_terminus_balance = self.erc20.balance_of(self.terminus.address)
        initial_controller_balance = self.erc20.balance_of(accounts[1].address)

        self.erc20.approve(self.terminus.address, 1000, {"from": accounts[1]})

        initial_total_pools = self.terminus.total_pools()

        self.terminus.create_simple_pool(10, {"from": accounts[1]})

        final_total_pools = self.terminus.total_pools()
        self.assertEqual(final_total_pools, initial_total_pools + 1)

        final_payer_balance = self.erc20.balance_of(accounts[1].address)
        intermediate_terminus_balance = self.erc20.balance_of(self.terminus.address)
        intermediate_controller_balance = self.erc20.balance_of(accounts[1].address)
        self.assertEqual(final_payer_balance, initial_payer_balance - 1000)
        self.assertEqual(intermediate_terminus_balance, initial_terminus_balance + 1000)
        self.assertEqual(
            intermediate_controller_balance, initial_controller_balance - 1000
        )

        with self.assertRaises(Exception):
            self.terminus.withdraw_payments(
                accounts[0].address, 1000, {"from": accounts[0]}
            )

        with self.assertRaises(Exception):
            self.terminus.withdraw_payments(
                accounts[1].address, 1000, {"from": accounts[0]}
            )

        with self.assertRaises(Exception):
            self.terminus.withdraw_payments(
                accounts[0].address, 1000, {"from": accounts[1]}
            )

        self.terminus.withdraw_payments(
            accounts[1].address, 1000, {"from": accounts[1]}
        )

        final_terminus_balance = self.erc20.balance_of(self.terminus.address)
        final_controller_balance = self.erc20.balance_of(accounts[1].address)
        self.assertEqual(final_terminus_balance, intermediate_terminus_balance - 1000)
        self.assertEqual(
            final_controller_balance, intermediate_controller_balance + 1000
        )

        with self.assertRaises(Exception):
            self.terminus.withdraw_payments(
                accounts[0].address,
                final_terminus_balance + 1000,
                {"from": accounts[0]},
            )

        pool_controller = self.terminus.terminus_pool_controller(final_total_pools)
        self.assertEqual(pool_controller, accounts[1].address)

        pool_capacity = self.terminus.terminus_pool_capacity(final_total_pools)
        self.assertEqual(pool_capacity, 10)


class TestPoolOperations(TerminusTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.erc20 = MockErc20.MockErc20(None)
        cls.erc20.deploy("test", "test", {"from": accounts[0]})
        cls.terminus.set_payment_token(cls.erc20.address, {"from": accounts[0]})
        cls.terminus.set_pool_base_price(1000, {"from": accounts[0]})
        cls.erc20.mint(accounts[1], 1000000, {"from": accounts[0]})
        cls.erc20.approve(cls.terminus.address, 1000000, {"from": accounts[1]})

        cls.terminus.set_controller(accounts[1].address, {"from": accounts[0]})

    def setUp(self) -> None:
        self.terminus.create_simple_pool(10, {"from": accounts[1]})

    def test_set_pool_controller(self):
        pool_id = self.terminus.total_pools()
        old_controller = accounts[1]
        new_controller = accounts[2]

        current_controller_address = self.terminus.terminus_pool_controller(pool_id)
        self.assertEqual(current_controller_address, old_controller.address)

        with self.assertRaises(Exception):
            self.terminus.set_pool_controller(
                pool_id, new_controller.address, {"from": new_controller}
            )
        current_controller_address = self.terminus.terminus_pool_controller(pool_id)
        self.assertEqual(current_controller_address, old_controller.address)

        self.terminus.set_pool_controller(
            pool_id, new_controller.address, {"from": old_controller}
        )
        current_controller_address = self.terminus.terminus_pool_controller(pool_id)
        self.assertEqual(current_controller_address, new_controller.address)

        with self.assertRaises(Exception):
            self.terminus.set_pool_controller(
                pool_id, old_controller.address, {"from": old_controller}
            )
        current_controller_address = self.terminus.terminus_pool_controller(pool_id)
        self.assertEqual(current_controller_address, new_controller.address)

        self.terminus.set_pool_controller(
            pool_id, old_controller.address, {"from": new_controller}
        )
        current_controller_address = self.terminus.terminus_pool_controller(pool_id)
        self.assertEqual(current_controller_address, old_controller.address)

    def test_mint(self):
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.assertEqual(balance, 1)

        supply = self.terminus.terminus_pool_supply(pool_id)
        self.assertEqual(supply, 1)

    def test_mint_fails_if_it_exceeds_capacity(self):
        pool_id = self.terminus.total_pools()
        with self.assertRaises(Exception):
            self.terminus.mint(accounts[2], pool_id, 11, b"", {"from": accounts[1]})

        balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.assertEqual(balance, 0)

        supply = self.terminus.terminus_pool_supply(pool_id)
        self.assertEqual(supply, 0)

    def test_mint_batch(self):
        pool_id = self.terminus.total_pools()
        self.terminus.mint_batch(
            accounts[2].address,
            pool_i_ds=[pool_id],
            amounts=[1],
            data=b"",
            transaction_config={"from": accounts[1]},
        )

        balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.assertEqual(balance, 1)

        supply = self.terminus.terminus_pool_supply(pool_id)
        self.assertEqual(supply, 1)

    def test_mint_batch_with_approval(self):
        pool_id = self.terminus.total_pools()

        self.assertFalse(self.terminus.is_approved_for_pool(pool_id, accounts[3]))
        self.assertFalse(self.terminus.is_approved_for_pool(pool_id - 1, accounts[3]))
        balances_before = [
            self.terminus.balance_of(accounts[2].address, pool_id),
            self.terminus.balance_of(accounts[2].address, pool_id - 1),
        ]
        supply_before = [
            self.terminus.terminus_pool_supply(pool_id),
            self.terminus.terminus_pool_supply(pool_id - 1),
        ]
        self.terminus.approve_for_pool(pool_id, accounts[3], {"from": accounts[1]})
        with self.assertRaises(Exception):
            self.terminus.mint_batch(
                accounts[2].address,
                pool_i_ds=[pool_id, pool_id - 1],
                amounts=[1, 1],
                data=b"",
                transaction_config={"from": accounts[3]},
            )

        self.terminus.approve_for_pool(pool_id - 1, accounts[3], {"from": accounts[1]})

        self.terminus.mint_batch(
            accounts[2].address,
            pool_i_ds=[pool_id, pool_id - 1],
            amounts=[1, 1],
            data=b"",
            transaction_config={"from": accounts[3]},
        )

        self.assertEqual(
            self.terminus.balance_of(accounts[2].address, pool_id),
            balances_before[0] + 1,
        )
        self.assertEqual(
            self.terminus.balance_of(accounts[2].address, pool_id - 1),
            balances_before[1] + 1,
        )

        self.assertEqual(
            self.terminus.terminus_pool_supply(pool_id), supply_before[0] + 1
        )
        self.assertEqual(
            self.terminus.terminus_pool_supply(pool_id - 1),
            supply_before[1] + 1,
        )

    def test_mint_batch_fails_if_it_exceeds_capacity(self):
        capacity = 10
        self.terminus.create_pool_v1(capacity, True, True, {"from": accounts[1]})
        pool_id = self.terminus.total_pools()
        with self.assertRaises(Exception):
            self.terminus.mint_batch(
                accounts[2].address,
                pool_i_ds=[pool_id, pool_id],
                amounts=[int(capacity / 2) + 1, int(capacity / 2) + 1],
                data=b"",
                transaction_config={"from": accounts[1]},
            )

        balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.assertEqual(balance, 0)

        supply = self.terminus.terminus_pool_supply(pool_id)
        self.assertEqual(supply, 0)

    def test_mint_batch_fails_if_it_exceeds_capacity_one_at_a_time(self):
        capacity = 10
        self.terminus.create_pool_v1(capacity, True, True, {"from": accounts[1]})
        pool_id = self.terminus.total_pools()
        with self.assertRaises(Exception):
            self.terminus.mint_batch(
                accounts[2].address,
                pool_i_ds=[pool_id for _ in range(capacity + 1)],
                amounts=[1 for _ in range(capacity + 1)],
                data=b"",
                transaction_config={"from": accounts[1]},
            )

        balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.assertEqual(balance, 0)

        supply = self.terminus.terminus_pool_supply(pool_id)
        self.assertEqual(supply, 0)

    def test_pool_mint_batch(self):
        pool_id = self.terminus.total_pools()
        target_accounts = [account.address for account in accounts[:5]]
        target_amounts = [1 for _ in accounts[:5]]
        num_accounts = len(accounts[:5])
        initial_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        initial_balances: List[int] = []
        for account in accounts[:5]:
            initial_balances.append(self.terminus.balance_of(account.address, pool_id))
        self.terminus.pool_mint_batch(
            pool_id, target_accounts, target_amounts, {"from": accounts[1]}
        )
        final_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        self.assertEqual(final_pool_supply, initial_pool_supply + num_accounts)
        for i, account in enumerate(accounts[:5]):
            final_balance = self.terminus.balance_of(account.address, pool_id)
            self.assertEqual(final_balance, initial_balances[i] + 1)

    def test_pool_mint_batch_as_contract_controller_not_pool_controller(self):
        pool_id = self.terminus.total_pools()
        target_accounts = [account.address for account in accounts[:5]]
        target_amounts = [1 for _ in accounts[:5]]
        initial_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        initial_balances: List[int] = []
        for account in accounts[:5]:
            initial_balances.append(self.terminus.balance_of(account.address, pool_id))
        with self.assertRaises(Exception):
            self.terminus.pool_mint_batch(
                pool_id, target_accounts, target_amounts, {"from": accounts[0]}
            )
        final_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        self.assertEqual(final_pool_supply, initial_pool_supply)
        for i, account in enumerate(accounts[:5]):
            final_balance = self.terminus.balance_of(account.address, pool_id)
            self.assertEqual(final_balance, initial_balances[i])

    def test_pool_mint_batch_as_unauthorized_third_party(self):
        pool_id = self.terminus.total_pools()
        target_accounts = [account.address for account in accounts[:5]]
        target_amounts = [1 for _ in accounts[:5]]
        initial_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        initial_balances: List[int] = []
        for account in accounts[:5]:
            initial_balances.append(self.terminus.balance_of(account.address, pool_id))
        with self.assertRaises(Exception):
            self.terminus.pool_mint_batch(
                pool_id, target_accounts, target_amounts, {"from": accounts[2]}
            )
        final_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        self.assertEqual(final_pool_supply, initial_pool_supply)
        for i, account in enumerate(accounts[:5]):
            final_balance = self.terminus.balance_of(account.address, pool_id)
            self.assertEqual(final_balance, initial_balances[i])

    def test_pool_mint_with_pool_approval(self):
        self.terminus.create_pool_v1(10, False, False, {"from": accounts[1]})
        pool_id = self.terminus.total_pools()

        self.assertFalse(
            self.terminus.is_approved_for_pool(pool_id, accounts[2].address)
        )
        with self.assertRaises(Exception):
            self.terminus.mint(
                accounts[2].address, pool_id, 1, b"", {"from": accounts[2]}
            )

        self.terminus.approve_for_pool(
            pool_id, accounts[2].address, {"from": accounts[1]}
        )
        supply_0 = self.terminus.terminus_pool_supply(pool_id)
        balance_0 = self.terminus.balance_of(accounts[2].address, pool_id)
        self.terminus.mint(accounts[2].address, pool_id, 1, b"", {"from": accounts[1]})
        balance_1 = self.terminus.balance_of(accounts[2].address, pool_id)
        supply_1 = self.terminus.terminus_pool_supply(pool_id)

        self.assertEqual(balance_1, balance_0 + 1)
        self.assertEqual(supply_0 + 1, supply_1)

    def test_pool_mint_batch_with_approval(self):
        pool_id = self.terminus.total_pools()
        target_accounts = [account.address for account in accounts[:5]]
        target_amounts = [1 for _ in accounts[:5]]
        num_accounts = len(accounts[:5])
        initial_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        initial_balances: List[int] = []
        for account in accounts[:5]:
            initial_balances.append(self.terminus.balance_of(account.address, pool_id))

        self.assertFalse(
            self.terminus.is_approved_for_pool(pool_id, accounts[2].address)
        )
        with self.assertRaises(Exception):
            self.terminus.pool_mint_batch(
                pool_id, target_accounts, target_amounts, {"from": accounts[2]}
            )
        self.terminus.approve_for_pool(
            pool_id, accounts[2].address, {"from": accounts[1]}
        )
        self.terminus.pool_mint_batch(
            pool_id, target_accounts, target_amounts, {"from": accounts[2]}
        )

        final_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        self.assertEqual(final_pool_supply, initial_pool_supply + num_accounts)
        for i, account in enumerate(accounts[:5]):
            final_balance = self.terminus.balance_of(account.address, pool_id)
            self.assertEqual(final_balance, initial_balances[i] + 1)

    def test_transfer(self):
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        initial_receiver_balance = self.terminus.balance_of(
            accounts[3].address, pool_id
        )

        self.terminus.safe_transfer_from(
            accounts[2].address,
            accounts[3].address,
            pool_id,
            1,
            b"",
            {"from": accounts[2]},
        )

        final_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        final_receiver_balance = self.terminus.balance_of(accounts[3].address, pool_id)

        self.assertEqual(final_sender_balance, initial_sender_balance - 1)
        self.assertEqual(final_receiver_balance, initial_receiver_balance + 1)

    def test_transfer_as_pool_controller(self):
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        initial_receiver_balance = self.terminus.balance_of(
            accounts[3].address, pool_id
        )

        self.terminus.safe_transfer_from(
            accounts[2].address,
            accounts[3].address,
            pool_id,
            1,
            b"",
            {"from": accounts[1]},
        )

        final_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        final_receiver_balance = self.terminus.balance_of(accounts[3].address, pool_id)

        self.assertEqual(final_sender_balance, initial_sender_balance - 1)
        self.assertEqual(final_receiver_balance, initial_receiver_balance + 1)

    def test_transfer_fails_as_controller_of_another_pool_with_no_approval(self):
        """
        Hacken.io auditors claimed that an address that controlled *some* pool could effect transfers
        on *any* pool.

        This test shows that this is not true.

        Exercises:
        - safeTransferFrom
        """
        # Ensure that accounts[1] is pool controller of *some* pool.
        self.terminus.create_pool_v1(100, True, True, {"from": accounts[1]})
        controlled_pool_id = self.terminus.total_pools()
        self.assertEqual(
            self.terminus.terminus_pool_controller(controlled_pool_id),
            accounts[1].address,
        )

        self.terminus.create_pool_v1(100, True, True, {"from": accounts[1]})
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        # Remove pool control from accounts[1]
        self.terminus.set_pool_controller(
            pool_id, accounts[4].address, {"from": accounts[1]}
        )

        initial_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        initial_receiver_balance = self.terminus.balance_of(
            accounts[3].address, pool_id
        )

        with self.assertRaises(VirtualMachineError):
            self.terminus.safe_transfer_from(
                accounts[2].address,
                accounts[3].address,
                pool_id,
                1,
                b"",
                {"from": accounts[1]},
            )

        final_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        final_receiver_balance = self.terminus.balance_of(accounts[3].address, pool_id)

        self.assertEqual(final_sender_balance, initial_sender_balance)
        self.assertEqual(final_receiver_balance, initial_receiver_balance)

    def test_transfer_fails_as_terminus_controller_with_no_approval(self):
        """
        Tests that neither Terminus controller *nor* pool controller can transfer a token on behalf of
        another address without explicit approval (using safeTransferFrom).

        Exercises:
        - safeTransferFrom
        """
        self.assertEqual(self.terminus.terminus_controller(), accounts[1].address)
        self.terminus.create_pool_v1(100, True, True, {"from": accounts[1]})
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        # Remove pool control from accounts[1]
        self.terminus.set_pool_controller(
            pool_id, accounts[4].address, {"from": accounts[1]}
        )

        initial_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        initial_receiver_balance = self.terminus.balance_of(
            accounts[3].address, pool_id
        )

        with self.assertRaises(VirtualMachineError):
            self.terminus.safe_transfer_from(
                accounts[2].address,
                accounts[3].address,
                pool_id,
                1,
                b"",
                {"from": accounts[1]},
            )

        final_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        final_receiver_balance = self.terminus.balance_of(accounts[3].address, pool_id)

        self.assertEqual(final_sender_balance, initial_sender_balance)
        self.assertEqual(final_receiver_balance, initial_receiver_balance)

    def test_transfer_as_unauthorized_recipient(self):
        self.terminus.create_pool_v1(2**256 - 1, True, True, {"from": accounts[1]})
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        initial_receiver_balance = self.terminus.balance_of(
            accounts[3].address, pool_id
        )

        with self.assertRaises(Exception):
            self.terminus.safe_transfer_from(
                accounts[2].address,
                accounts[3].address,
                pool_id,
                1,
                b"",
                {"from": accounts[3]},
            )

        final_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        final_receiver_balance = self.terminus.balance_of(accounts[3].address, pool_id)

        self.assertEqual(final_sender_balance, initial_sender_balance)
        self.assertEqual(final_receiver_balance, initial_receiver_balance)

    def test_transfer_as_authorized_recipient(self):
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        initial_receiver_balance = self.terminus.balance_of(
            accounts[3].address, pool_id
        )

        self.terminus.approve_for_pool(
            pool_id, accounts[3].address, {"from": accounts[1]}
        )
        self.terminus.safe_transfer_from(
            accounts[2].address,
            accounts[3].address,
            pool_id,
            1,
            b"",
            {"from": accounts[3]},
        )

        final_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        final_receiver_balance = self.terminus.balance_of(accounts[3].address, pool_id)

        self.assertEqual(final_sender_balance, initial_sender_balance - 1)
        self.assertEqual(final_receiver_balance, initial_receiver_balance + 1)

    def test_transfer_as_approved_operator(self):
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        initial_receiver_balance = self.terminus.balance_of(
            accounts[3].address, pool_id
        )

        # It is very important to revoke this approval from accounts[3] as accounts[3] tries to initiate
        # transfers from accounts[2] in other tests.
        self.terminus.set_approval_for_all(
            accounts[3].address, True, {"from": accounts[2]}
        )

        try:
            self.terminus.safe_transfer_from(
                accounts[2].address,
                accounts[3].address,
                pool_id,
                1,
                b"",
                {"from": accounts[3]},
            )
        finally:
            self.terminus.set_approval_for_all(
                accounts[3].address, False, {"from": accounts[2]}
            )

        final_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        final_receiver_balance = self.terminus.balance_of(accounts[3].address, pool_id)

        self.assertEqual(final_sender_balance, initial_sender_balance - 1)
        self.assertEqual(final_receiver_balance, initial_receiver_balance + 1)

        # Check that accounts[3] is no longer approved for all pools by accounts[2] (for other tests to)
        # run correctly.
        self.assertFalse(
            self.terminus.is_approved_for_all(accounts[2].address, accounts[3].address)
        )

    def test_transfer_as_unauthorized_unrelated_party(self):
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        initial_receiver_balance = self.terminus.balance_of(
            accounts[3].address, pool_id
        )

        with self.assertRaises(Exception):
            self.terminus.safe_transfer_from(
                accounts[2].address,
                accounts[3].address,
                pool_id,
                1,
                b"",
                {"from": accounts[4]},
            )

        final_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        final_receiver_balance = self.terminus.balance_of(accounts[3].address, pool_id)

        self.assertEqual(final_sender_balance, initial_sender_balance)
        self.assertEqual(final_receiver_balance, initial_receiver_balance)

    def test_transfer_as_authorized_unrelated_party(self):
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        initial_receiver_balance = self.terminus.balance_of(
            accounts[3].address, pool_id
        )

        self.terminus.approve_for_pool(
            pool_id, accounts[4].address, {"from": accounts[1]}
        )
        self.terminus.safe_transfer_from(
            accounts[2].address,
            accounts[3].address,
            pool_id,
            1,
            b"",
            {"from": accounts[4]},
        )

        final_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        final_receiver_balance = self.terminus.balance_of(accounts[3].address, pool_id)

        self.assertEqual(final_sender_balance, initial_sender_balance - 1)
        self.assertEqual(final_receiver_balance, initial_receiver_balance + 1)

    def test_burn_fails_as_token_owner(self):
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        initial_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        with self.assertRaises(Exception):
            self.terminus.burn(accounts[2].address, pool_id, 1, {"from": accounts[2]})

        final_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        final_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.assertEqual(final_pool_supply, initial_pool_supply)
        self.assertEqual(final_owner_balance, initial_owner_balance)

    def test_burn_fails_as_pool_controller(self):
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        initial_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        with self.assertRaises(Exception):
            self.terminus.burn(accounts[2].address, pool_id, 1, {"from": accounts[1]})

        final_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        final_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.assertEqual(final_pool_supply, initial_pool_supply)
        self.assertEqual(final_owner_balance, initial_owner_balance)

    def test_burn_fails_as_third_party(self):
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        initial_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        with self.assertRaises(Exception):
            self.terminus.burn(accounts[2].address, pool_id, 1, {"from": accounts[3]})

        final_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        final_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.assertEqual(final_pool_supply, initial_pool_supply)
        self.assertEqual(final_owner_balance, initial_owner_balance)

    def test_burn_fails_as_authorized_third_party(self):
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        initial_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.terminus.approve_for_pool(
            pool_id, accounts[3].address, {"from": accounts[1]}
        )
        with self.assertRaises(Exception):
            self.terminus.burn(accounts[2].address, pool_id, 1, {"from": accounts[3]})

        final_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        final_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.assertEqual(final_pool_supply, initial_pool_supply)
        self.assertEqual(final_owner_balance, initial_owner_balance)

    def test_pool_approval(self):
        controller = accounts[1]
        operator = accounts[2]
        user = accounts[3]

        # TODO(zomglings): We should test the Terminus controller permissions on the same contract.
        # Currently, controller is both pool controller AND Terminus controller. In a more proper test,
        # these would be different accounts.

        # TODO(zomglings): Tested manually that changing burnable below from True to False results in
        # the right reversion when we try to burn these tokens on-chain. This should be a separate
        # test case that runs *automatically*.
        self.terminus.create_pool_v1(100, True, True, {"from": controller})
        pool_id = self.terminus.total_pools()
        self.terminus.mint(controller.address, pool_id, 5, "", {"from": controller})
        self.terminus.mint(operator.address, pool_id, 5, "", {"from": controller})
        self.terminus.mint(user.address, pool_id, 5, "", {"from": controller})

        controller_balance_0 = self.terminus.balance_of(controller.address, pool_id)
        operator_balance_0 = self.terminus.balance_of(operator.address, pool_id)
        user_balance_0 = self.terminus.balance_of(user.address, pool_id)

        self.assertFalse(self.terminus.is_approved_for_pool(pool_id, operator.address))

        with self.assertRaises(VirtualMachineError):
            self.terminus.mint(controller.address, pool_id, 1, "", {"from": operator})

        with self.assertRaises(VirtualMachineError):
            self.terminus.mint(operator.address, pool_id, 1, "", {"from": operator})

        with self.assertRaises(VirtualMachineError):
            self.terminus.mint(user.address, pool_id, 1, "", {"from": operator})

        controller_balance_1 = self.terminus.balance_of(controller.address, pool_id)
        operator_balance_1 = self.terminus.balance_of(operator.address, pool_id)
        user_balance_1 = self.terminus.balance_of(user.address, pool_id)

        self.assertEqual(controller_balance_1, controller_balance_0)
        self.assertEqual(operator_balance_1, operator_balance_0)
        self.assertEqual(user_balance_1, user_balance_0)

        with self.assertRaises(VirtualMachineError):
            self.terminus.burn(controller.address, pool_id, 1, {"from": operator})

        self.terminus.burn(operator.address, pool_id, 1, {"from": operator})

        with self.assertRaises(VirtualMachineError):
            self.terminus.burn(user.address, pool_id, 1, {"from": operator})

        controller_balance_2 = self.terminus.balance_of(controller.address, pool_id)
        operator_balance_2 = self.terminus.balance_of(operator.address, pool_id)
        user_balance_2 = self.terminus.balance_of(user.address, pool_id)

        self.assertEqual(controller_balance_2, controller_balance_1)
        self.assertEqual(operator_balance_2, operator_balance_1 - 1)
        self.assertEqual(user_balance_2, user_balance_1)

        with self.assertRaises(VirtualMachineError):
            self.terminus.approve_for_pool(pool_id, operator, {"from": operator})

        self.terminus.approve_for_pool(pool_id, operator, {"from": accounts[1]})

        self.assertTrue(self.terminus.is_approved_for_pool(pool_id, operator.address))

        self.terminus.mint(controller.address, pool_id, 1, "", {"from": operator})
        self.terminus.mint(operator.address, pool_id, 1, "", {"from": operator})
        self.terminus.mint(user.address, pool_id, 1, "", {"from": operator})

        controller_balance_3 = self.terminus.balance_of(controller.address, pool_id)
        operator_balance_3 = self.terminus.balance_of(operator.address, pool_id)
        user_balance_3 = self.terminus.balance_of(user.address, pool_id)

        self.assertEqual(controller_balance_3, controller_balance_2 + 1)
        self.assertEqual(operator_balance_3, operator_balance_2 + 1)
        self.assertEqual(user_balance_3, user_balance_2 + 1)

        self.terminus.burn(controller.address, pool_id, 1, {"from": operator})
        self.terminus.burn(operator.address, pool_id, 1, {"from": operator})
        self.terminus.burn(user.address, pool_id, 1, {"from": operator})

        controller_balance_4 = self.terminus.balance_of(controller.address, pool_id)
        operator_balance_4 = self.terminus.balance_of(operator.address, pool_id)
        user_balance_4 = self.terminus.balance_of(user.address, pool_id)

        self.assertEqual(controller_balance_4, controller_balance_3 - 1)
        self.assertEqual(operator_balance_4, operator_balance_3 - 1)
        self.assertEqual(user_balance_4, user_balance_3 - 1)

        with self.assertRaises(VirtualMachineError):
            self.terminus.unapprove_for_pool(pool_id, operator, {"from": operator})

        self.assertTrue(self.terminus.is_approved_for_pool(pool_id, operator.address))

        self.terminus.unapprove_for_pool(pool_id, operator, {"from": controller})

        self.assertFalse(self.terminus.is_approved_for_pool(pool_id, operator.address))

        with self.assertRaises(VirtualMachineError):
            self.terminus.mint(controller.address, pool_id, 1, "", {"from": operator})

        with self.assertRaises(VirtualMachineError):
            self.terminus.mint(operator.address, pool_id, 1, "", {"from": operator})

        with self.assertRaises(VirtualMachineError):
            self.terminus.mint(user.address, pool_id, 1, "", {"from": operator})

        controller_balance_5 = self.terminus.balance_of(controller.address, pool_id)
        operator_balance_5 = self.terminus.balance_of(operator.address, pool_id)
        user_balance_5 = self.terminus.balance_of(user.address, pool_id)

        self.assertEqual(controller_balance_5, controller_balance_4)
        self.assertEqual(operator_balance_5, operator_balance_4)
        self.assertEqual(user_balance_5, user_balance_4)

        with self.assertRaises(VirtualMachineError):
            self.terminus.burn(controller.address, pool_id, 1, {"from": operator})

        self.terminus.burn(operator.address, pool_id, 1, {"from": operator})

        with self.assertRaises(VirtualMachineError):
            self.terminus.burn(user.address, pool_id, 1, {"from": operator})

        controller_balance_6 = self.terminus.balance_of(controller.address, pool_id)
        operator_balance_6 = self.terminus.balance_of(operator.address, pool_id)
        user_balance_6 = self.terminus.balance_of(user.address, pool_id)

        self.assertEqual(controller_balance_6, controller_balance_5)
        self.assertEqual(operator_balance_6, operator_balance_5 - 1)
        self.assertEqual(user_balance_6, user_balance_5)


class TestPoolCreation(TestPoolOperations):
    def setUp(self):
        self.terminus.create_pool_v1(10, True, False, {"from": accounts[1]})

    def test_nontransferable_pool(self):
        self.terminus.create_pool_v1(10, False, False, {"from": accounts[1]})
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        initial_receiver_balance = self.terminus.balance_of(
            accounts[3].address, pool_id
        )

        with self.assertRaises(Exception):
            self.terminus.safe_transfer_from(
                accounts[2].address,
                accounts[3].address,
                pool_id,
                1,
                b"",
                {"from": accounts[2]},
            )

        final_sender_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        final_receiver_balance = self.terminus.balance_of(accounts[3].address, pool_id)

        self.assertEqual(final_sender_balance, initial_sender_balance)
        self.assertEqual(final_receiver_balance, initial_receiver_balance)

    def test_pool_state_view_methods(self):
        nontransferable_nonburnable_pool_uri = "https://example.com/ff.json"
        self.terminus.create_pool_v2(
            10,
            False,
            False,
            nontransferable_nonburnable_pool_uri,
            {"from": accounts[1]},
        )
        nontransferable_nonburnable_pool_id = self.terminus.total_pools()
        self.assertFalse(
            self.terminus.pool_is_transferable(nontransferable_nonburnable_pool_id)
        )
        self.assertFalse(
            self.terminus.pool_is_burnable(nontransferable_nonburnable_pool_id)
        )
        self.assertEqual(
            self.terminus.uri(nontransferable_nonburnable_pool_id),
            nontransferable_nonburnable_pool_uri,
        )

        transferable_nonburnable_pool_uri = "https://example.com/tf.json"
        self.terminus.create_pool_v2(
            10, True, False, transferable_nonburnable_pool_uri, {"from": accounts[1]}
        )
        transferable_nonburnable_pool_id = self.terminus.total_pools()
        self.assertTrue(
            self.terminus.pool_is_transferable(transferable_nonburnable_pool_id)
        )
        self.assertFalse(
            self.terminus.pool_is_burnable(transferable_nonburnable_pool_id)
        )
        self.assertEqual(
            self.terminus.uri(transferable_nonburnable_pool_id),
            transferable_nonburnable_pool_uri,
        )

        transferable_burnable_pool_uri = "https://example.com/tt.json"
        self.terminus.create_pool_v2(
            10, True, True, transferable_burnable_pool_uri, {"from": accounts[1]}
        )
        transferable_burnable_pool_id = self.terminus.total_pools()
        self.assertTrue(
            self.terminus.pool_is_transferable(transferable_burnable_pool_id)
        )
        self.assertTrue(self.terminus.pool_is_burnable(transferable_burnable_pool_id))
        self.assertEqual(
            self.terminus.uri(transferable_burnable_pool_id),
            transferable_burnable_pool_uri,
        )

        nontransferable_burnable_pool_uri = "https://example.com/ft.json"
        self.terminus.create_pool_v2(
            10, False, True, nontransferable_burnable_pool_uri, {"from": accounts[1]}
        )
        nontransferable_burnable_pool_id = self.terminus.total_pools()
        self.assertFalse(
            self.terminus.pool_is_transferable(nontransferable_burnable_pool_id)
        )
        self.assertTrue(
            self.terminus.pool_is_burnable(nontransferable_burnable_pool_id)
        )
        self.assertEqual(
            self.terminus.uri(nontransferable_burnable_pool_id),
            nontransferable_burnable_pool_uri,
        )

    def test_pool_state_setters(self):
        self.terminus.create_pool_v1(10, False, False, {"from": accounts[1]})
        pool_id = self.terminus.total_pools()
        self.assertEqual(
            self.terminus.terminus_pool_controller(pool_id), accounts[1].address
        )

        self.assertFalse(self.terminus.pool_is_transferable(pool_id))
        self.assertFalse(self.terminus.pool_is_burnable(pool_id))

        self.terminus.set_pool_transferable(pool_id, True, {"from": accounts[1]})
        self.assertTrue(self.terminus.pool_is_transferable(pool_id))
        self.assertFalse(self.terminus.pool_is_burnable(pool_id))

        self.terminus.set_pool_burnable(pool_id, True, {"from": accounts[1]})
        self.assertTrue(self.terminus.pool_is_transferable(pool_id))
        self.assertTrue(self.terminus.pool_is_burnable(pool_id))

        self.terminus.set_pool_transferable(pool_id, False, {"from": accounts[1]})
        self.assertFalse(self.terminus.pool_is_transferable(pool_id))
        self.assertTrue(self.terminus.pool_is_burnable(pool_id))

        self.terminus.set_pool_burnable(pool_id, False, {"from": accounts[1]})
        self.assertFalse(self.terminus.pool_is_transferable(pool_id))
        self.assertFalse(self.terminus.pool_is_burnable(pool_id))

    def test_pool_state_setters_do_not_allow_noncontroller_to_set_parameters(self):
        self.terminus.create_pool_v1(10, False, False, {"from": accounts[1]})
        pool_id = self.terminus.total_pools()
        self.assertEqual(
            self.terminus.terminus_pool_controller(pool_id), accounts[1].address
        )

        self.assertFalse(self.terminus.pool_is_transferable(pool_id))
        self.assertFalse(self.terminus.pool_is_burnable(pool_id))

        with self.assertRaises(VirtualMachineError):
            self.terminus.set_pool_transferable(pool_id, True, {"from": accounts[2]})

        with self.assertRaises(VirtualMachineError):
            self.terminus.set_pool_burnable(pool_id, True, {"from": accounts[2]})

        self.assertFalse(self.terminus.pool_is_transferable(pool_id))
        self.assertFalse(self.terminus.pool_is_burnable(pool_id))

    def test_burnable_pool_burn_as_token_owner(self):
        self.terminus.create_pool_v1(10, True, True, {"from": accounts[1]})
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        initial_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.terminus.burn(accounts[2].address, pool_id, 1, {"from": accounts[2]})

        final_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        final_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.assertEqual(final_pool_supply, initial_pool_supply - 1)
        self.assertEqual(final_owner_balance, initial_owner_balance - 1)

    def test_burnable_pool_burn_as_pool_controller(self):
        self.terminus.create_pool_v1(10, True, True, {"from": accounts[1]})
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        initial_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.terminus.burn(accounts[2].address, pool_id, 1, {"from": accounts[1]})

        final_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        final_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.assertEqual(final_pool_supply, initial_pool_supply - 1)
        self.assertEqual(final_owner_balance, initial_owner_balance - 1)

    def test_burnable_pool_burn_as_authorized_third_party(self):
        self.terminus.create_pool_v1(10, True, True, {"from": accounts[1]})
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        initial_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.terminus.approve_for_pool(
            pool_id, accounts[3].address, {"from": accounts[1]}
        )
        self.terminus.burn(accounts[2].address, pool_id, 1, {"from": accounts[3]})

        final_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        final_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.assertEqual(final_pool_supply, initial_pool_supply - 1)
        self.assertEqual(final_owner_balance, initial_owner_balance - 1)

    def test_burnable_pool_burn_as_unauthorized_third_party(self):
        self.terminus.create_pool_v1(10, True, True, {"from": accounts[1]})
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        initial_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        with self.assertRaises(Exception):
            self.terminus.burn(accounts[2].address, pool_id, 1, {"from": accounts[3]})

        final_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        final_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.assertEqual(final_pool_supply, initial_pool_supply)
        self.assertEqual(final_owner_balance, initial_owner_balance)

    def test_nontransferable_pool_safe_transfer_from(self):
        self.terminus.create_pool_v1(10, False, False, {"from": accounts[1]})
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        initial_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        with self.assertRaises(Exception):
            self.terminus.safe_transfer_from(
                accounts[2].address,
                accounts[3].address,
                pool_id,
                1,
                b"",
                {"from": accounts[2]},
            )

        final_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        final_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.assertEqual(final_pool_supply, initial_pool_supply)
        self.assertEqual(final_owner_balance, initial_owner_balance)

    def test_nontransferable_pool_safe_batch_transfer_from(self):
        self.terminus.create_pool_v1(10, False, False, {"from": accounts[1]})
        pool_id = self.terminus.total_pools()
        self.terminus.mint(accounts[2], pool_id, 1, b"", {"from": accounts[1]})

        initial_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        initial_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        with self.assertRaises(Exception):
            self.terminus.safe_batch_transfer_from(
                accounts[2].address,
                accounts[3].address,
                [pool_id],
                [1],
                b"",
                {"from": accounts[2]},
            )

        final_pool_supply = self.terminus.terminus_pool_supply(pool_id)
        final_owner_balance = self.terminus.balance_of(accounts[2].address, pool_id)
        self.assertEqual(final_pool_supply, initial_pool_supply)
        self.assertEqual(final_owner_balance, initial_owner_balance)


if __name__ == "__main__":
    unittest.main()
