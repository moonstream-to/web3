import unittest
from typing import Dict, Any

from brownie import accounts, network, web3 as web3_client
from brownie.exceptions import VirtualMachineError
from moonworm.watch import _fetch_events_chunk

from . import Dropper, MockTerminus, MockErc20, MockERC721

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


class DropperTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            network.connect()
        except:
            pass

        # ERC20 setup
        cls.erc20_contract = MockErc20.MockErc20(None)
        cls.erc20_contract.deploy({"from": accounts[0]})
        cls.erc20_contract.mint(accounts[0], 100 * 10 ** 18, {"from": accounts[0]})

        # ERC721 setup
        cls.nft_contract = MockERC721.MockERC721(None)
        cls.nft_contract.deploy({"from": accounts[0]})
        cls.nft_contract.mint(accounts[0].address, 1, {"from": accounts[0]})
        cls.nft_contract.mint(accounts[0].address, 2, {"from": accounts[0]})
        cls.nft_contract.mint(accounts[0].address, 3, {"from": accounts[0]})
        cls.nft_contract.mint(accounts[0].address, 4, {"from": accounts[0]})

        # Terminus/ERC1155 setup
        cls.terminus = MockTerminus.MockTerminus(None)
        cls.terminus.deploy({"from": accounts[0]})
        cls.terminus.set_payment_token(
            cls.erc20_contract.address, {"from": accounts[0]}
        )
        cls.terminus.set_pool_base_price(1, {"from": accounts[0]})
        cls.erc20_contract.approve(
            cls.terminus.address, 100 * 10 ** 18, {"from": accounts[0]}
        )
        cls.terminus.create_pool_v1(2 ** 256 - 1, True, True, {"from": accounts[0]})
        cls.terminus_pool_id = cls.terminus.total_pools()

        # Dropper deployment
        cls.dropper = Dropper.Dropper(None)
        cls.dropper.deploy({"from": accounts[0]})

        # Create signer accounts
        cls.signer_0 = accounts.add()
        cls.signer_1 = accounts.add()

    def create_claim_and_return_claim_id(self, *args, **kwargs) -> int:
        tx_receipt = self.dropper.create_claim(*args, **kwargs)
        claim_created_event_abi = None
        for item in self.dropper.abi:
            if item["type"] == "event" and item["name"] == "ClaimCreated":
                claim_created_event_abi = item
        self.assertIsNotNone(claim_created_event_abi)
        events = _fetch_events_chunk(
            web3_client,
            claim_created_event_abi,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )
        self.assertEqual(len(events), 1)
        return events[0]["args"]["claimId"]


class DropperClaimTests(DropperTestCase):
    def test_claim_creation(self):
        num_claims_0 = self.dropper.num_claims()
        claim_id = self.create_claim_and_return_claim_id(
            20, self.erc20_contract.address, 0, 1, {"from": accounts[0]}
        )
        num_claims_1 = self.dropper.num_claims()
        self.assertEqual(num_claims_1, num_claims_0 + 1)
        self.assertEqual(claim_id, num_claims_1)

        claim_info = self.dropper.get_claim(claim_id)
        self.assertEqual(claim_info, (20, self.erc20_contract.address, 0, 1))

    def test_claim_creation_fails_if_unknown_token_type(self):
        UNKNOWN_TOKEN_TYPE = 43
        num_claims_0 = self.dropper.num_claims()
        with self.assertRaises(VirtualMachineError):
            self.dropper.create_claim(
                43, self.erc20_contract.address, 0, 1, {"from": accounts[0]}
            )
        num_claims_1 = self.dropper.num_claims()
        self.assertEqual(num_claims_1, num_claims_0)

    def test_claim_creation_fails_from_non_owner(self):
        num_claims_0 = self.dropper.num_claims()
        with self.assertRaises(VirtualMachineError):
            self.dropper.create_claim(
                20, self.erc20_contract.address, 0, 1, {"from": accounts[1]}
            )
        num_claims_1 = self.dropper.num_claims()
        self.assertEqual(num_claims_1, num_claims_0)

    def test_claim_status_for_new_claim(self):
        claim_id = self.create_claim_and_return_claim_id(
            20, self.erc20_contract.address, 0, 1, {"from": accounts[0]}
        )
        self.assertTrue(self.dropper.claim_status(claim_id))

    def test_claim_status_can_be_changed_by_owner(self):
        claim_id = self.create_claim_and_return_claim_id(
            20, self.erc20_contract.address, 0, 1, {"from": accounts[0]}
        )
        self.assertTrue(self.dropper.claim_status(claim_id))

        self.dropper.set_claim_status(claim_id, False, {"from": accounts[0]})
        self.assertFalse(self.dropper.claim_status(claim_id))

    def test_claim_status_cannot_be_changed_by_non_owner(self):
        claim_id = self.create_claim_and_return_claim_id(
            20, self.erc20_contract.address, 0, 1, {"from": accounts[0]}
        )
        self.assertTrue(self.dropper.claim_status(claim_id))

        with self.assertRaises(VirtualMachineError):
            self.dropper.set_claim_status(claim_id, False, {"from": accounts[1]})

        self.assertTrue(self.dropper.claim_status(claim_id))

    def test_owner_can_set_signer(self):
        claim_id = self.create_claim_and_return_claim_id(
            20, self.erc20_contract.address, 0, 1, {"from": accounts[0]}
        )
        self.assertEqual(self.dropper.get_signer_for_claim(claim_id), ZERO_ADDRESS)

        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )
        self.assertEqual(
            self.dropper.get_signer_for_claim(claim_id), self.signer_0.address
        )

    def test_non_owner_cannot_set_signer(self):
        claim_id = self.create_claim_and_return_claim_id(
            20, self.erc20_contract.address, 0, 1, {"from": accounts[0]}
        )
        self.assertEqual(self.dropper.get_signer_for_claim(claim_id), ZERO_ADDRESS)

        with self.assertRaises(VirtualMachineError):
            self.dropper.set_signer_for_claim(
                claim_id, self.signer_0.address, {"from": accounts[1]}
            )
        self.assertEqual(self.dropper.get_signer_for_claim(claim_id), ZERO_ADDRESS)


class DropperWithdrawalTests(DropperTestCase):
    def test_withdraw_erc20(self):
        balance_funder_0 = self.erc20_contract.balance_of(accounts[0].address)
        balance_dropper_0 = self.erc20_contract.balance_of(self.dropper.address)

        self.assertGreaterEqual(balance_funder_0, 2)

        self.erc20_contract.transfer(self.dropper.address, 2, {"from": accounts[0]})

        balance_funder_1 = self.erc20_contract.balance_of(accounts[0].address)
        balance_dropper_1 = self.erc20_contract.balance_of(self.dropper.address)

        self.assertEqual(balance_funder_1, balance_funder_0 - 2)
        self.assertEqual(balance_dropper_1, balance_dropper_0 + 2)

        self.dropper.withdraw_erc20(
            self.erc20_contract.address, 1, {"from": accounts[0]}
        )

        balance_funder_2 = self.erc20_contract.balance_of(accounts[0].address)
        balance_dropper_2 = self.erc20_contract.balance_of(self.dropper.address)

        self.assertEqual(balance_funder_2, balance_funder_1 + 1)
        self.assertEqual(balance_dropper_2, balance_dropper_1 - 1)

    def test_non_owner_cannot_withdraw_erc20(self):
        balance_funder_0 = self.erc20_contract.balance_of(accounts[0].address)
        self.assertGreaterEqual(balance_funder_0, 1)

        balance_attacker_0 = self.erc20_contract.balance_of(accounts[1].address)

        self.erc20_contract.transfer(self.dropper.address, 2, {"from": accounts[0]})

        balance_dropper_0 = self.erc20_contract.balance_of(self.dropper.address)

        with self.assertRaises(VirtualMachineError):
            self.dropper.withdraw_erc20(
                self.erc20_contract.address, 1, {"from": accounts[1]}
            )

        balance_attacker_1 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_1 = self.erc20_contract.balance_of(self.dropper.address)

        self.assertEqual(balance_attacker_1, balance_attacker_0)
        self.assertEqual(balance_dropper_1, balance_dropper_0)

    def test_withdraw_erc721(self):
        num_tokens = self.nft_contract.total_supply()
        token_id = num_tokens + 1
        self.nft_contract.mint(accounts[0].address, token_id, {"from": accounts[0]})

        self.assertEqual(self.nft_contract.owner_of(token_id), accounts[0].address)

        self.nft_contract.transfer_from(
            accounts[0].address, self.dropper.address, token_id, {"from": accounts[0]}
        )

        self.assertEqual(self.nft_contract.owner_of(token_id), self.dropper.address)

        self.dropper.withdraw_erc721(
            self.nft_contract.address, token_id, {"from": accounts[0]}
        )

        self.assertEqual(self.nft_contract.owner_of(token_id), accounts[0].address)

    def test_non_owner_cannot_withdraw_erc721(self):
        num_tokens = self.nft_contract.total_supply()
        token_id = num_tokens + 1
        self.nft_contract.mint(accounts[0].address, token_id, {"from": accounts[0]})

        self.assertEqual(self.nft_contract.owner_of(token_id), accounts[0].address)

        self.nft_contract.transfer_from(
            accounts[0].address, self.dropper.address, token_id, {"from": accounts[0]}
        )

        self.assertEqual(self.nft_contract.owner_of(token_id), self.dropper.address)

        with self.assertRaises(VirtualMachineError):
            self.dropper.withdraw_erc721(
                self.nft_contract.address, token_id, {"from": accounts[1]}
            )

        self.assertEqual(self.nft_contract.owner_of(token_id), self.dropper.address)

    def test_withdraw_erc1155(self):
        amount = 34

        self.terminus.mint(
            self.dropper.address,
            self.terminus_pool_id,
            amount,
            "",
            {"from": accounts[0]},
        )

        balance_owner_0 = self.terminus.balance_of(accounts[0], self.terminus_pool_id)
        balance_dropper_0 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )

        self.dropper.withdraw_erc1155(
            self.terminus.address, self.terminus_pool_id, amount, {"from": accounts[0]}
        )

        balance_owner_1 = self.terminus.balance_of(accounts[0], self.terminus_pool_id)
        balance_dropper_1 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )

        self.assertEqual(balance_owner_1, balance_owner_0 + amount)
        self.assertEqual(balance_dropper_1, balance_dropper_0 - amount)

    def test_non_owner_cannot_withdraw_erc1155(self):
        self.terminus.mint(
            self.dropper.address, self.terminus_pool_id, 1, "", {"from": accounts[0]}
        )

        balance_owner_0 = self.terminus.balance_of(accounts[0], self.terminus_pool_id)
        balance_dropper_0 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        balance_attacker_0 = self.terminus.balance_of(
            accounts[1], self.terminus_pool_id
        )

        with self.assertRaises(VirtualMachineError):
            self.dropper.withdraw_erc1155(
                self.terminus.address, self.terminus_pool_id, 1, {"from": accounts[1]}
            )

        balance_owner_1 = self.terminus.balance_of(accounts[0], self.terminus_pool_id)
        balance_dropper_1 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        balance_attacker_1 = self.terminus.balance_of(
            accounts[1], self.terminus_pool_id
        )

        self.assertEqual(balance_owner_1, balance_owner_0)
        self.assertEqual(balance_dropper_1, balance_dropper_0)
        self.assertEqual(balance_attacker_1, balance_attacker_0)