from multiprocessing import pool
import unittest
from typing import Dict, Any

from brownie import accounts, network, web3 as web3_client
from brownie.exceptions import VirtualMachineError
from brownie.network import chain
from eth_account._utils.signing import sign_message_hash
import eth_keys
from hexbytes import HexBytes
from moonworm.watch import _fetch_events_chunk

from . import Dropper, MockTerminus, MockErc20, MockERC721

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def sign_message(message_hash, signer):
    eth_private_key = eth_keys.keys.PrivateKey(HexBytes(signer.private_key))
    message_hash_bytes = HexBytes(message_hash)
    _, _, _, signed_message_bytes = sign_message_hash(
        eth_private_key, message_hash_bytes
    )
    return signed_message_bytes.hex()


class DropperTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            network.connect()
        except:
            pass

        # ERC20 setup
        cls.erc20_contract = MockErc20.MockErc20(None)
        cls.erc20_contract.deploy("test", "test", {"from": accounts[0]})
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

        # create dropper own pool
        cls.terminus.create_pool_v1(500000, True, True, {"from": accounts[0]})

        cls.mintable_terminus_pool_id = cls.terminus.total_pools()

        # Dropper deployment
        cls.dropper = Dropper.Dropper(None)
        cls.dropper.deploy({"from": accounts[0]})

        cls.TERMINUS_MINTABLE_TYPE = int(cls.dropper.terminus_mintable_type())
        cls.terminus.set_pool_controller(
            cls.mintable_terminus_pool_id, cls.dropper.address, {"from": accounts[0]}
        )

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

    def test_owner_can_set_claim_uri(self):
        claim_id = self.create_claim_and_return_claim_id(
            20, self.erc20_contract.address, 0, 1, {"from": accounts[0]}
        )
        self.assertEqual(self.dropper.claim_uri(claim_id), "")
        self.dropper.set_claim_uri(
            claim_id, "https://example.com", {"from": accounts[0]}
        )
        self.assertEqual(self.dropper.claim_uri(claim_id), "https://example.com")

    def test_non_owner_cannot_set_claim_uri(self):
        claim_id = self.create_claim_and_return_claim_id(
            20, self.erc20_contract.address, 0, 1, {"from": accounts[0]}
        )
        self.assertEqual(self.dropper.claim_uri(claim_id), "")
        with self.assertRaises(VirtualMachineError):
            self.dropper.set_claim_uri(
                claim_id, "https://example.com", {"from": accounts[1]}
            )
        self.assertEqual(self.dropper.claim_uri(claim_id), "")


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


class DropperClaimERC20Tests(DropperTestCase):
    def test_claim_erc20(self):
        reward = 3
        self.erc20_contract.mint(self.dropper.address, 100, {"from": accounts[0]})
        claim_id = self.create_claim_and_return_claim_id(
            20, self.erc20_contract.address, 0, reward, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        balance_claimant_0 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_0 = self.erc20_contract.balance_of(self.dropper.address)

        self.dropper.claim(
            claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
        )
        balance_claimant_1 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_1 = self.erc20_contract.balance_of(self.dropper.address)

        self.assertEqual(balance_claimant_1, balance_claimant_0 + reward)
        self.assertEqual(balance_dropper_1, balance_dropper_0 - reward)

    def test_claim_erc20_with_custom_amount(self):
        default_reward = 3
        custom_reward = 89
        self.erc20_contract.mint(self.dropper.address, 100, {"from": accounts[0]})
        claim_id = self.create_claim_and_return_claim_id(
            20, self.erc20_contract.address, 0, default_reward, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, custom_reward
        )
        signed_message = sign_message(message_hash, self.signer_0)

        balance_claimant_0 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_0 = self.erc20_contract.balance_of(self.dropper.address)

        self.dropper.claim(
            claim_id,
            block_deadline,
            custom_reward,
            signed_message,
            {"from": accounts[1]},
        )
        balance_claimant_1 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_1 = self.erc20_contract.balance_of(self.dropper.address)

        self.assertEqual(balance_claimant_1, balance_claimant_0 + custom_reward)
        self.assertEqual(balance_dropper_1, balance_dropper_0 - custom_reward)

    def test_claim_erc20_fails_if_block_deadline_exceeded(self):
        reward = 5
        self.erc20_contract.mint(self.dropper.address, 100, {"from": accounts[0]})
        claim_id = self.create_claim_and_return_claim_id(
            20, self.erc20_contract.address, 0, reward, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block - 1

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        balance_claimant_0 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_0 = self.erc20_contract.balance_of(self.dropper.address)

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
            )

        balance_claimant_1 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_1 = self.erc20_contract.balance_of(self.dropper.address)

        self.assertEqual(balance_claimant_1, balance_claimant_0)
        self.assertEqual(balance_dropper_1, balance_dropper_0)

    def test_claim_erc20_fails_if_incorrect_amount(self):
        reward = 5
        self.erc20_contract.mint(self.dropper.address, 100, {"from": accounts[0]})
        claim_id = self.create_claim_and_return_claim_id(
            20, self.erc20_contract.address, 0, reward, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        balance_claimant_0 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_0 = self.erc20_contract.balance_of(self.dropper.address)

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id,
                block_deadline,
                reward + 1,
                signed_message,
                {"from": accounts[1]},
            )

        balance_claimant_1 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_1 = self.erc20_contract.balance_of(self.dropper.address)

        self.assertEqual(balance_claimant_1, balance_claimant_0)
        self.assertEqual(balance_dropper_1, balance_dropper_0)

    def test_claim_erc20_fails_if_wrong_claimant(self):
        reward = 6
        self.erc20_contract.mint(self.dropper.address, 100, {"from": accounts[0]})
        claim_id = self.create_claim_and_return_claim_id(
            20, self.erc20_contract.address, 0, reward, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        balance_attacker_0 = self.erc20_contract.balance_of(accounts[2].address)
        balance_claimant_0 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_0 = self.erc20_contract.balance_of(self.dropper.address)

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[2]}
            )

        balance_attacker_1 = self.erc20_contract.balance_of(accounts[2].address)
        balance_claimant_1 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_1 = self.erc20_contract.balance_of(self.dropper.address)

        self.assertEqual(balance_attacker_1, balance_attacker_0)
        self.assertEqual(balance_claimant_1, balance_claimant_0)
        self.assertEqual(balance_dropper_1, balance_dropper_0)

    def test_claim_erc20_fails_if_wrong_signer(self):
        reward = 7
        self.erc20_contract.mint(self.dropper.address, 100, {"from": accounts[0]})
        claim_id = self.create_claim_and_return_claim_id(
            20, self.erc20_contract.address, 0, reward, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_1)

        balance_claimant_0 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_0 = self.erc20_contract.balance_of(self.dropper.address)

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[2]}
            )

        balance_claimant_1 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_1 = self.erc20_contract.balance_of(self.dropper.address)

        self.assertEqual(balance_claimant_1, balance_claimant_0)
        self.assertEqual(balance_dropper_1, balance_dropper_0)

    def test_claim_erc20_fails_on_repeated_attempts_with_same_signed_message(self):
        reward = 9
        self.erc20_contract.mint(self.dropper.address, 100, {"from": accounts[0]})
        claim_id = self.create_claim_and_return_claim_id(
            20, self.erc20_contract.address, 0, reward, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block + 1000

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        balance_claimant_0 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_0 = self.erc20_contract.balance_of(self.dropper.address)

        self.dropper.claim(
            claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
        )
        balance_claimant_1 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_1 = self.erc20_contract.balance_of(self.dropper.address)

        self.assertEqual(balance_claimant_1, balance_claimant_0 + reward)
        self.assertEqual(balance_dropper_1, balance_dropper_0 - reward)

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
            )

        balance_claimant_2 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_2 = self.erc20_contract.balance_of(self.dropper.address)

        self.assertEqual(balance_claimant_2, balance_claimant_1)
        self.assertEqual(balance_dropper_2, balance_dropper_1)

    def test_claim_erc20_fails_on_repeated_attempts_with_different_signed_messages(
        self,
    ):
        reward = 9
        self.erc20_contract.mint(self.dropper.address, 100, {"from": accounts[0]})
        claim_id = self.create_claim_and_return_claim_id(
            20, self.erc20_contract.address, 0, reward, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        balance_claimant_0 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_0 = self.erc20_contract.balance_of(self.dropper.address)

        self.dropper.claim(
            claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
        )
        balance_claimant_1 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_1 = self.erc20_contract.balance_of(self.dropper.address)

        self.assertEqual(balance_claimant_1, balance_claimant_0 + reward)
        self.assertEqual(balance_dropper_1, balance_dropper_0 - reward)

        current_block = len(chain)
        block_deadline = current_block

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
            )

        balance_claimant_2 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_2 = self.erc20_contract.balance_of(self.dropper.address)

        self.assertEqual(balance_claimant_2, balance_claimant_1)
        self.assertEqual(balance_dropper_2, balance_dropper_1)

    def test_claim_erc20_fails_when_insufficient_balance(self):
        reward = 33
        # Drain Dropper of ERC20 tokens
        self.dropper.withdraw_erc20(
            self.erc20_contract.address,
            self.erc20_contract.balance_of(self.dropper.address),
            {"from": accounts[0]},
        )
        claim_id = self.create_claim_and_return_claim_id(
            20, self.erc20_contract.address, 0, reward, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        balance_claimant_0 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_0 = self.erc20_contract.balance_of(self.dropper.address)

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
            )

        balance_claimant_1 = self.erc20_contract.balance_of(accounts[1].address)
        balance_dropper_1 = self.erc20_contract.balance_of(self.dropper.address)

        self.assertEqual(balance_claimant_1, balance_claimant_0)
        self.assertEqual(balance_dropper_1, balance_dropper_0)


class DropperClaimERC721Tests(DropperTestCase):
    def test_claim_erc721(self):
        token_id = 103
        self.nft_contract.mint(self.dropper.address, token_id, {"from": accounts[0]})
        claim_id = self.create_claim_and_return_claim_id(
            721, self.nft_contract.address, token_id, 1, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        self.assertEqual(self.nft_contract.owner_of(token_id), self.dropper.address)

        self.dropper.claim(
            claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
        )
        self.assertEqual(self.nft_contract.owner_of(token_id), accounts[1].address)

    def test_claim_erc721_with_custom_amount(self):
        token_id = 1003
        custom_amount = 79
        self.nft_contract.mint(self.dropper.address, token_id, {"from": accounts[0]})
        claim_id = self.create_claim_and_return_claim_id(
            721, self.nft_contract.address, token_id, 1, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, custom_amount
        )
        signed_message = sign_message(message_hash, self.signer_0)

        self.assertEqual(self.nft_contract.owner_of(token_id), self.dropper.address)

        self.dropper.claim(
            claim_id,
            block_deadline,
            custom_amount,
            signed_message,
            {"from": accounts[1]},
        )
        self.assertEqual(self.nft_contract.owner_of(token_id), accounts[1].address)

    def test_claim_erc721_fails_if_block_deadline_exceeded(self):
        token_id = 105
        self.nft_contract.mint(self.dropper.address, token_id, {"from": accounts[0]})
        claim_id = self.create_claim_and_return_claim_id(
            721, self.nft_contract.address, token_id, 1, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block - 1

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        self.assertEqual(self.nft_contract.owner_of(token_id), self.dropper.address)

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
            )

        self.assertEqual(self.nft_contract.owner_of(token_id), self.dropper.address)

    def test_claim_erc721_fails_if_incorrect_amount(self):
        token_id = 1005
        self.nft_contract.mint(self.dropper.address, token_id, {"from": accounts[0]})
        claim_id = self.create_claim_and_return_claim_id(
            721, self.nft_contract.address, token_id, 1, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        self.assertEqual(self.nft_contract.owner_of(token_id), self.dropper.address)

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 1, signed_message, {"from": accounts[1]}
            )

        self.assertEqual(self.nft_contract.owner_of(token_id), self.dropper.address)

    def test_claim_erc721_fails_if_wrong_claimant(self):
        token_id = 106
        self.nft_contract.mint(self.dropper.address, token_id, {"from": accounts[0]})
        claim_id = self.create_claim_and_return_claim_id(
            721, self.nft_contract.address, token_id, 1, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        self.assertEqual(self.nft_contract.owner_of(token_id), self.dropper.address)

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[2]}
            )

        self.assertEqual(self.nft_contract.owner_of(token_id), self.dropper.address)

    def test_claim_erc721_fails_if_wrong_signer(self):
        token_id = 107
        self.nft_contract.mint(self.dropper.address, token_id, {"from": accounts[0]})
        claim_id = self.create_claim_and_return_claim_id(
            721, self.nft_contract.address, token_id, 1, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_1)

        self.assertEqual(self.nft_contract.owner_of(token_id), self.dropper.address)

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[2]}
            )

        self.assertEqual(self.nft_contract.owner_of(token_id), self.dropper.address)

    def test_claim_erc721_fails_on_repeated_attempts_with_same_signed_message(self):
        token_id = 109
        self.nft_contract.mint(self.dropper.address, token_id, {"from": accounts[0]})
        claim_id = self.create_claim_and_return_claim_id(
            721, self.nft_contract.address, token_id, 1, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block + 1000

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        self.assertEqual(self.nft_contract.owner_of(token_id), self.dropper.address)

        self.dropper.claim(
            claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
        )
        self.assertEqual(self.nft_contract.owner_of(token_id), accounts[1].address)

        self.nft_contract.safe_transfer_from(
            accounts[1].address,
            self.dropper.address,
            token_id,
            "",
            {"from": accounts[1]},
        )

        self.assertEqual(self.nft_contract.owner_of(token_id), self.dropper.address)

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
            )

        self.assertEqual(self.nft_contract.owner_of(token_id), self.dropper.address)

    def test_claim_erc721_fails_on_repeated_attempts_with_different_signed_messages(
        self,
    ):
        token_id = 110
        self.nft_contract.mint(self.dropper.address, token_id, {"from": accounts[0]})
        claim_id = self.create_claim_and_return_claim_id(
            721, self.nft_contract.address, token_id, 1, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        self.dropper.claim(
            claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
        )
        self.assertEqual(self.nft_contract.owner_of(token_id), accounts[1].address)

        self.nft_contract.safe_transfer_from(
            accounts[1].address,
            self.dropper.address,
            token_id,
            "",
            {"from": accounts[1]},
        )

        current_block = len(chain)
        block_deadline = current_block

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
            )

        self.assertEqual(self.nft_contract.owner_of(token_id), self.dropper.address)

    def test_claim_erc721_fails_if_dropper_not_owner(self):
        token_id = 111
        self.nft_contract.mint(accounts[0].address, token_id, {"from": accounts[0]})
        self.assertNotEqual(self.nft_contract.owner_of(token_id), self.dropper.address)
        claim_id = self.create_claim_and_return_claim_id(
            721, self.nft_contract.address, token_id, 1, {"from": accounts[0]}
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
            )

        self.assertNotEqual(self.nft_contract.owner_of(token_id), accounts[1].address)
        self.assertNotEqual(self.nft_contract.owner_of(token_id), self.dropper.address)


class DropperClaimERC1155Tests(DropperTestCase):
    def test_claim_erc1155(self):
        reward = 3
        self.terminus.mint(
            self.dropper.address,
            self.terminus_pool_id,
            10 * reward,
            "",
            {"from": accounts[0]},
        )
        claim_id = self.create_claim_and_return_claim_id(
            1155,
            self.terminus.address,
            self.terminus_pool_id,
            reward,
            {"from": accounts[0]},
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )
        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed
        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)
        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_0 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        self.dropper.claim(
            claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
        )
        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_1 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        self.assertEqual(balance_claimant_1, balance_claimant_0 + reward)
        self.assertEqual(balance_dropper_1, balance_dropper_0 - reward)

    def test_claim_erc1155_with_custom_amount(self):
        default_reward = 3
        custom_reward = default_reward + 1
        self.terminus.mint(
            self.dropper.address,
            self.terminus_pool_id,
            10 * custom_reward,
            "",
            {"from": accounts[0]},
        )
        claim_id = self.create_claim_and_return_claim_id(
            1155,
            self.terminus.address,
            self.terminus_pool_id,
            default_reward,
            {"from": accounts[0]},
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )
        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed
        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, custom_reward
        )
        signed_message = sign_message(message_hash, self.signer_0)
        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_0 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        self.dropper.claim(
            claim_id,
            block_deadline,
            custom_reward,
            signed_message,
            {"from": accounts[1]},
        )
        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_1 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        self.assertEqual(balance_claimant_1, balance_claimant_0 + custom_reward)
        self.assertEqual(balance_dropper_1, balance_dropper_0 - custom_reward)

    def test_claim_erc1155_fails_if_block_deadline_exceeded(self):
        reward = 5
        self.terminus.mint(
            self.dropper.address,
            self.terminus_pool_id,
            10 * reward,
            "",
            {"from": accounts[0]},
        )
        claim_id = self.create_claim_and_return_claim_id(
            1155,
            self.terminus.address,
            self.terminus_pool_id,
            reward,
            {"from": accounts[0]},
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )
        current_block = len(chain)
        block_deadline = current_block - 1
        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)
        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_0 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
            )
        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_1 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        self.assertEqual(balance_claimant_1, balance_claimant_0)
        self.assertEqual(balance_dropper_1, balance_dropper_0)

    def test_claim_erc1155_fails_if_incorrect_amount(self):
        reward = 5
        self.terminus.mint(
            self.dropper.address,
            self.terminus_pool_id,
            10 * reward,
            "",
            {"from": accounts[0]},
        )
        claim_id = self.create_claim_and_return_claim_id(
            1155,
            self.terminus.address,
            self.terminus_pool_id,
            reward,
            {"from": accounts[0]},
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )
        current_block = len(chain)
        block_deadline = current_block
        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)
        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_0 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, reward, signed_message, {"from": accounts[1]}
            )
        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_1 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        self.assertEqual(balance_claimant_1, balance_claimant_0)
        self.assertEqual(balance_dropper_1, balance_dropper_0)

    def test_claim_erc1155_fails_if_wrong_claimant(self):
        reward = 6
        self.terminus.mint(
            self.dropper.address,
            self.terminus_pool_id,
            10 * reward,
            "",
            {"from": accounts[0]},
        )
        claim_id = self.create_claim_and_return_claim_id(
            1155,
            self.terminus.address,
            self.terminus_pool_id,
            reward,
            {"from": accounts[0]},
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )
        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed
        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)
        balance_attacker_0 = self.terminus.balance_of(
            accounts[2].address, self.terminus_pool_id
        )
        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_0 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[2]}
            )
        balance_attacker_1 = self.terminus.balance_of(
            accounts[2].address, self.terminus_pool_id
        )
        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_1 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        self.assertEqual(balance_attacker_1, balance_attacker_0)
        self.assertEqual(balance_claimant_1, balance_claimant_0)
        self.assertEqual(balance_dropper_1, balance_dropper_0)

    def test_claim_erc1155_fails_if_wrong_signer(self):
        reward = 7
        self.terminus.mint(
            self.dropper.address,
            self.terminus_pool_id,
            10 * reward,
            "",
            {"from": accounts[0]},
        )
        claim_id = self.create_claim_and_return_claim_id(
            1155,
            self.terminus.address,
            self.terminus_pool_id,
            reward,
            {"from": accounts[0]},
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )
        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed
        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_1)
        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_0 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[2]}
            )
        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_1 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        self.assertEqual(balance_claimant_1, balance_claimant_0)
        self.assertEqual(balance_dropper_1, balance_dropper_0)

    def test_claim_erc1155_fails_on_repeated_attempts_with_same_signed_message(self):
        reward = 9
        self.terminus.mint(
            self.dropper.address,
            self.terminus_pool_id,
            10 * reward,
            "",
            {"from": accounts[0]},
        )
        claim_id = self.create_claim_and_return_claim_id(
            1155,
            self.terminus.address,
            self.terminus_pool_id,
            reward,
            {"from": accounts[0]},
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )
        current_block = len(chain)
        block_deadline = current_block + 1000
        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)
        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_0 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        self.dropper.claim(
            claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
        )
        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_1 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        self.assertEqual(balance_claimant_1, balance_claimant_0 + reward)
        self.assertEqual(balance_dropper_1, balance_dropper_0 - reward)
        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
            )
        balance_claimant_2 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_2 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        self.assertEqual(balance_claimant_2, balance_claimant_1)
        self.assertEqual(balance_dropper_2, balance_dropper_1)

    def test_claim_erc1155_fails_on_repeated_attempts_with_different_signed_messages(
        self,
    ):
        reward = 9
        self.terminus.mint(
            self.dropper.address,
            self.terminus_pool_id,
            10 * reward,
            "",
            {"from": accounts[0]},
        )
        claim_id = self.create_claim_and_return_claim_id(
            1155,
            self.terminus.address,
            self.terminus_pool_id,
            reward,
            {"from": accounts[0]},
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )
        current_block = len(chain)
        block_deadline = current_block
        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)
        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_0 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        self.dropper.claim(
            claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
        )
        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_1 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        self.assertEqual(balance_claimant_1, balance_claimant_0 + reward)
        self.assertEqual(balance_dropper_1, balance_dropper_0 - reward)
        current_block = len(chain)
        block_deadline = current_block
        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)
        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
            )
        balance_claimant_2 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_2 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        self.assertEqual(balance_claimant_2, balance_claimant_1)
        self.assertEqual(balance_dropper_2, balance_dropper_1)

    def test_claim_erc1155_fails_when_insufficient_balance(self):
        reward = 33
        # Drain Dropper of ERC1155 tokens
        self.dropper.withdraw_erc1155(
            self.terminus.address,
            self.terminus_pool_id,
            self.terminus.balance_of(self.dropper.address, self.terminus_pool_id),
            {"from": accounts[0]},
        )
        claim_id = self.create_claim_and_return_claim_id(
            1155,
            self.terminus.address,
            self.terminus_pool_id,
            reward,
            {"from": accounts[0]},
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )
        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed
        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)
        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_0 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
            )
        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, self.terminus_pool_id
        )
        balance_dropper_1 = self.terminus.balance_of(
            self.dropper.address, self.terminus_pool_id
        )
        self.assertEqual(balance_claimant_1, balance_claimant_0)
        self.assertEqual(balance_dropper_1, balance_dropper_0)


class DropperClaimERC1155MintableTests(DropperTestCase):
    def test_claim_erc1155(self):
        reward = 3
        claim_id = self.create_claim_and_return_claim_id(
            self.TERMINUS_MINTABLE_TYPE,
            self.terminus.address,
            self.mintable_terminus_pool_id,
            reward,
            {"from": accounts[0]},
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )

        pool_supply_0 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        self.dropper.claim(
            claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
        )

        pool_supply_1 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )
        self.assertEqual(balance_claimant_1, balance_claimant_0 + reward)
        self.assertEqual(pool_supply_1, pool_supply_0 + reward)

    def test_claim_erc1155_with_custom_amount(self):
        default_reward = 3
        custom_reward = default_reward + 1
        claim_id = self.create_claim_and_return_claim_id(
            self.TERMINUS_MINTABLE_TYPE,
            self.terminus.address,
            self.mintable_terminus_pool_id,
            default_reward,
            {"from": accounts[0]},
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, custom_reward
        )
        signed_message = sign_message(message_hash, self.signer_0)

        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )

        pool_supply_0 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        self.dropper.claim(
            claim_id,
            block_deadline,
            custom_reward,
            signed_message,
            {"from": accounts[1]},
        )

        pool_supply_1 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )
        self.assertEqual(balance_claimant_1, balance_claimant_0 + custom_reward)
        self.assertEqual(pool_supply_1, pool_supply_0 + custom_reward)

    def test_claim_erc1155_fails_if_dropper_does_not_have_pool_control(self):
        reward = 33

        # create pool wich is owned by the dropper
        self.terminus.create_pool_v1(2 ** 256 - 1, True, True, {"from": accounts[0]})
        terminus_pool_which_is_owned_by_dropper_id = self.terminus.total_pools()

        self.terminus.set_pool_controller(
            terminus_pool_which_is_owned_by_dropper_id,
            self.dropper.address,
            {"from": accounts[0]},
        )

        claim_id = self.create_claim_and_return_claim_id(
            self.TERMINUS_MINTABLE_TYPE,
            self.terminus.address,
            terminus_pool_which_is_owned_by_dropper_id,
            reward,
            {"from": accounts[0]},
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, terminus_pool_which_is_owned_by_dropper_id
        )

        balance_second_claimant_0 = self.terminus.balance_of(
            accounts[2].address, terminus_pool_which_is_owned_by_dropper_id
        )

        pool_supply_0 = self.terminus.terminus_pool_supply(
            terminus_pool_which_is_owned_by_dropper_id
        )

        self.dropper.claim(
            claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
        )

        pool_supply_1 = self.terminus.terminus_pool_supply(
            terminus_pool_which_is_owned_by_dropper_id
        )

        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, terminus_pool_which_is_owned_by_dropper_id
        )

        self.assertEqual(balance_claimant_1, balance_claimant_0 + reward)
        self.assertEqual(pool_supply_1, pool_supply_0 + reward)

        self.dropper.surrender_pool_control(
            terminus_pool_which_is_owned_by_dropper_id,
            self.terminus.address,
            ZERO_ADDRESS,
            {"from": accounts[0]},
        )
        self.assertEqual(
            self.terminus.terminus_pool_controller(
                terminus_pool_which_is_owned_by_dropper_id
            ),
            ZERO_ADDRESS,
        )

        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[2].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[2]}
            )

        pool_supply_2 = self.terminus.terminus_pool_supply(
            terminus_pool_which_is_owned_by_dropper_id
        )
        balance_second_claimant_2 = self.terminus.balance_of(
            accounts[2].address, terminus_pool_which_is_owned_by_dropper_id
        )

        self.assertEqual(balance_second_claimant_2, balance_second_claimant_0)
        self.assertEqual(pool_supply_2, pool_supply_1)

    def test_claim_erc1155_fails_if_block_deadline_exceeded(self):
        reward = 5
        claim_id = self.create_claim_and_return_claim_id(
            self.TERMINUS_MINTABLE_TYPE,
            self.terminus.address,
            self.mintable_terminus_pool_id,
            reward,
            {"from": accounts[0]},
        )

        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block - 1

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )

        pool_supply_0 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
            )

        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )

        pool_supply_1 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        self.assertEqual(balance_claimant_1, balance_claimant_0)
        self.assertEqual(pool_supply_1, pool_supply_0)

    def test_claim_erc1155_fails_if_incorrect_amount(self):
        reward = 5
        claim_id = self.create_claim_and_return_claim_id(
            self.TERMINUS_MINTABLE_TYPE,
            self.terminus.address,
            self.mintable_terminus_pool_id,
            reward,
            {"from": accounts[0]},
        )

        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )

        pool_supply_0 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 1, signed_message, {"from": accounts[1]}
            )

        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )

        pool_supply_1 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        self.assertEqual(balance_claimant_1, balance_claimant_0)
        self.assertEqual(pool_supply_1, pool_supply_0)

    def test_claim_erc1155_fails_if_wrong_claimant(self):
        reward = 6

        claim_id = self.create_claim_and_return_claim_id(
            self.TERMINUS_MINTABLE_TYPE,
            self.terminus.address,
            self.mintable_terminus_pool_id,
            reward,
            {"from": accounts[0]},
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        balance_attacker_0 = self.terminus.balance_of(
            accounts[2].address, self.mintable_terminus_pool_id
        )
        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )

        pool_supply_0 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[2]}
            )

        balance_attacker_1 = self.terminus.balance_of(
            accounts[2].address, self.mintable_terminus_pool_id
        )
        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )
        pool_supply_1 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        self.assertEqual(balance_attacker_1, balance_attacker_0)
        self.assertEqual(balance_claimant_1, balance_claimant_0)
        self.assertEqual(pool_supply_1, pool_supply_0)

    def test_claim_erc1155_fails_if_wrong_signer(self):
        reward = 7
        claim_id = self.create_claim_and_return_claim_id(
            self.TERMINUS_MINTABLE_TYPE,
            self.terminus.address,
            self.mintable_terminus_pool_id,
            reward,
            {"from": accounts[0]},
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block  # since blocks are 0-indexed

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_1)

        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )
        pool_supply_0 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[2]}
            )

        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )

        pool_supply_1 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        self.assertEqual(balance_claimant_1, balance_claimant_0)
        self.assertEqual(pool_supply_1, pool_supply_0)

    def test_claim_erc1155_fails_on_repeated_attempts_with_same_signed_message(self):
        reward = 9
        claim_id = self.create_claim_and_return_claim_id(
            self.TERMINUS_MINTABLE_TYPE,
            self.terminus.address,
            self.mintable_terminus_pool_id,
            reward,
            {"from": accounts[0]},
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block + 1000

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )
        pool_supply_0 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        self.dropper.claim(
            claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
        )

        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )

        pool_supply_1 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        self.assertEqual(balance_claimant_1, balance_claimant_0 + reward)
        self.assertEqual(pool_supply_1, pool_supply_0 + reward)

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
            )

        balance_claimant_2 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )

        pool_supply_2 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        self.assertEqual(balance_claimant_2, balance_claimant_1)
        self.assertEqual(pool_supply_2, pool_supply_1)

    def test_claim_erc1155_fails_on_repeated_attempts_with_different_signed_messages(
        self,
    ):
        reward = 9
        claim_id = self.create_claim_and_return_claim_id(
            self.TERMINUS_MINTABLE_TYPE,
            self.terminus.address,
            self.mintable_terminus_pool_id,
            reward,
            {"from": accounts[0]},
        )
        self.dropper.set_signer_for_claim(
            claim_id, self.signer_0.address, {"from": accounts[0]}
        )

        current_block = len(chain)
        block_deadline = current_block

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        balance_claimant_0 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )

        pool_supply_0 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        self.dropper.claim(
            claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
        )

        balance_claimant_1 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )

        pool_supply_1 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        self.assertEqual(balance_claimant_1, balance_claimant_0 + reward)
        self.assertEqual(pool_supply_1, pool_supply_0 + reward)

        current_block = len(chain)
        block_deadline = current_block

        message_hash = self.dropper.claim_message_hash(
            claim_id, accounts[1].address, block_deadline, 0
        )
        signed_message = sign_message(message_hash, self.signer_0)

        with self.assertRaises(VirtualMachineError):
            self.dropper.claim(
                claim_id, block_deadline, 0, signed_message, {"from": accounts[1]}
            )

        balance_claimant_2 = self.terminus.balance_of(
            accounts[1].address, self.mintable_terminus_pool_id
        )
        pool_supply_2 = self.terminus.terminus_pool_supply(
            self.mintable_terminus_pool_id
        )

        self.assertEqual(balance_claimant_2, balance_claimant_1)
        self.assertEqual(pool_supply_2, pool_supply_1)


class DropperPoolControllerTest(DropperTestCase):
    def test_move_pool_controller_fails_on_invalid_pool_id(self):
        # create pool wich is not owned by the dropper
        self.terminus.create_pool_v1(500000, True, True, {"from": accounts[0]})
        terminus_pool_which_is_not_owned_by_dropper_id = self.terminus.total_pools()

        with self.assertRaises(VirtualMachineError):
            self.dropper.surrender_pool_control(
                terminus_pool_which_is_not_owned_by_dropper_id,
                self.terminus.address,
                "0x0000000000000000000000000000000000000000",
                {"from": accounts[0]},
            )

        self.assertEqual(
            self.terminus.terminus_pool_controller(
                terminus_pool_which_is_not_owned_by_dropper_id
            ),
            accounts[0].address,
        )

    def test_move_pool_controller_to_new_owner(self):
        # create pool wich is owned by the dropper
        self.terminus.create_pool_v1(500000, True, True, {"from": accounts[0]})
        terminus_pool_which_is_owned_by_dropper_id = self.terminus.total_pools()

        self.terminus.set_pool_controller(
            terminus_pool_which_is_owned_by_dropper_id,
            self.dropper.address,
            {"from": accounts[0]},
        )

        self.dropper.surrender_pool_control(
            terminus_pool_which_is_owned_by_dropper_id,
            self.terminus.address,
            accounts[1].address,
            {"from": accounts[0]},
        )

        self.assertEqual(
            self.terminus.terminus_pool_controller(
                terminus_pool_which_is_owned_by_dropper_id
            ),
            accounts[1].address,
        )
