import unittest

import math

from brownie import accounts, network, web3 as web3_client, ZERO_ADDRESS
from brownie.exceptions import VirtualMachineError
from moonworm.watch import _fetch_events_chunk
import web3

from . import GOFPFacet, MockTerminus, MockErc20, MockERC721, GOFPPredicates
from .core import gofp_gogogo

MAX_UINT = 2**256 - 1

SESSION_CREATED_EVENT_ABI = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "sessionId",
            "type": "uint256",
        },
        {
            "indexed": True,
            "internalType": "address",
            "name": "playerTokenAddress",
            "type": "address",
        },
        {
            "indexed": True,
            "internalType": "address",
            "name": "paymentTokenAddress",
            "type": "address",
        },
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "paymentAmount",
            "type": "uint256",
        },
        {
            "indexed": False,
            "internalType": "string",
            "name": "uri",
            "type": "string",
        },
        {
            "indexed": False,
            "internalType": "bool",
            "name": "active",
            "type": "bool",
        },
        {
            "indexed": False,
            "internalType": "bool",
            "name": "isForgiving",
            "type": "bool",
        },
    ],
    "name": "SessionCreated",
    "type": "event",
}

SESSION_ACTIVATED_EVENT_ABI = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "sessionId",
            "type": "uint256",
        },
        {
            "indexed": False,
            "internalType": "bool",
            "name": "active",
            "type": "bool",
        },
    ],
    "name": "SessionActivated",
    "type": "event",
}

SESSION_CHOOSING_ACTIVATED_EVENT_ABI = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "sessionId",
            "type": "uint256",
        },
        {
            "indexed": False,
            "internalType": "bool",
            "name": "isChoosingActive",
            "type": "bool",
        },
    ],
    "name": "SessionChoosingActivated",
    "type": "event",
}

SESSION_URI_CHANGED_EVENT_ABI = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "sessionId",
            "type": "uint256",
        },
        {"indexed": False, "internalType": "string", "name": "uri", "type": "string"},
    ],
    "name": "SessionUriChanged",
    "type": "event",
}

PATH_REGISTERED_EVENT_ABI = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "sessionId",
            "type": "uint256",
        },
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "stage",
            "type": "uint256",
        },
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "path",
            "type": "uint256",
        },
    ],
    "name": "PathRegistered",
    "type": "event",
}

STAGE_REWARD_CHANGED_ABI = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "sessionId",
            "type": "uint256",
        },
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "stage",
            "type": "uint256",
        },
        {
            "indexed": False,
            "internalType": "address",
            "name": "terminusAddress",
            "type": "address",
        },
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "terminusPoolId",
            "type": "uint256",
        },
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "rewardAmount",
            "type": "uint256",
        },
    ],
    "name": "StageRewardChanged",
    "type": "event",
}

PATH_REWARD_CHANGED_ABI = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "sessionId",
            "type": "uint256",
        },
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "stage",
            "type": "uint256",
        },
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "path",
            "type": "uint256",
        },
        {
            "indexed": False,
            "internalType": "address",
            "name": "terminusAddress",
            "type": "address",
        },
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "terminusPoolId",
            "type": "uint256",
        },
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "rewardAmount",
            "type": "uint256",
        },
    ],
    "name": "PathRewardChanged",
    "type": "event",
}

PATH_CHOSEN_EVENT_ABI = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "sessionId",
            "type": "uint256",
        },
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "tokenId",
            "type": "uint256",
        },
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "stage",
            "type": "uint256",
        },
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "path",
            "type": "uint256",
        },
    ],
    "name": "PathChosen",
    "type": "event",
}

ERC1155_TRANSFER_SINGLE_EVENT = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "address",
            "name": "operator",
            "type": "address",
        },
        {"indexed": True, "internalType": "address", "name": "from", "type": "address"},
        {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
        {"indexed": False, "internalType": "uint256", "name": "id", "type": "uint256"},
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "value",
            "type": "uint256",
        },
    ],
    "name": "TransferSingle",
    "type": "event",
}


class GOFPTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            network.connect()
        except:
            pass

        cls.owner = accounts[0]
        cls.owner_tx_config = {"from": cls.owner}

        cls.game_master = accounts[1]
        cls.player = accounts[2]
        cls.random_person = accounts[3]

        cls.nft = MockERC721.MockERC721(None)
        cls.nft.deploy(cls.owner_tx_config)

        cls.gofp_predicates = GOFPPredicates.GOFPPredicates(None)
        cls.gofp_predicates.deploy(cls.owner_tx_config)

        cls.terminus = MockTerminus.MockTerminus(None)
        cls.terminus.deploy(cls.owner_tx_config)

        cls.payment_token = MockErc20.MockErc20(None)
        cls.payment_token.deploy("lol", "lol", cls.owner_tx_config)

        cls.terminus.set_payment_token(cls.payment_token.address, cls.owner_tx_config)
        cls.terminus.set_pool_base_price(1, cls.owner_tx_config)

        cls.payment_token.mint(cls.owner.address, 999999, cls.owner_tx_config)

        cls.payment_token.approve(
            cls.terminus.address, 2**256 - 1, cls.owner_tx_config
        )

        cls.terminus.create_pool_v1(1, False, True, cls.owner_tx_config)
        cls.admin_pool_id = cls.terminus.total_pools()

        cls.terminus.create_pool_v1(MAX_UINT, True, True, cls.owner_tx_config)
        cls.reward_pool_id = cls.terminus.total_pools()

        cls.terminus.create_pool_v1(MAX_UINT, True, True, cls.owner_tx_config)
        cls.reward_2_pool_id = cls.terminus.total_pools()

        cls.terminus.create_pool_v1(MAX_UINT, True, True, cls.owner_tx_config)
        cls.reward_3_pool_id = cls.terminus.total_pools()

        cls.terminus.create_pool_v1(MAX_UINT, True, True, cls.owner_tx_config)
        cls.reward_4_pool_id = cls.terminus.total_pools()

        # It is important for some of the tests that the owner of the contract *not* be the game master.
        cls.terminus.mint(
            cls.game_master.address, cls.admin_pool_id, 1, "", cls.owner_tx_config
        )

        # Mint NFTs and ERC20 tokens to player
        for i in range(1, 6):
            cls.nft.mint(cls.player.address, i, {"from": cls.owner})

        cls.payment_token.mint(cls.player.address, 10**6, {"from": cls.owner})

        cls.deployed_contracts = gofp_gogogo(
            cls.terminus.address, cls.admin_pool_id, cls.owner_tx_config
        )
        cls.gofp = GOFPFacet.GOFPFacet(cls.deployed_contracts["contracts"]["Diamond"])

        # Set gofp as approved pool operator for reward pool
        cls.terminus.approve_for_pool(
            cls.reward_pool_id, cls.gofp.address, cls.owner_tx_config
        )
        cls.terminus.approve_for_pool(
            cls.reward_2_pool_id, cls.gofp.address, cls.owner_tx_config
        )
        cls.terminus.approve_for_pool(
            cls.reward_3_pool_id, cls.gofp.address, cls.owner_tx_config
        )
        cls.terminus.approve_for_pool(
            cls.reward_4_pool_id, cls.gofp.address, cls.owner_tx_config
        )

    def test_admin_terminus_info(self):
        terminus_info = self.gofp.admin_terminus_info()
        self.assertEqual(terminus_info[0], self.terminus.address)
        self.assertEqual(terminus_info[1], self.admin_pool_id)


class TestAdminFlow(GOFPTestCase):
    def test_create_session_then_get_session_active(self):
        num_sessions_0 = self.gofp.num_sessions()

        expected_payment_amount = 42
        expected_uri = (
            "https://example.com/test_create_session_then_get_session_active.json"
        )
        expected_stages = (5, 5, 3, 3, 2)
        expected_is_active = True

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            expected_payment_amount,
            expected_is_active,
            expected_uri,
            expected_stages,
            False,
            {"from": self.game_master},
        )

        num_sessions_1 = self.gofp.num_sessions()
        self.assertEqual(num_sessions_1, num_sessions_0 + 1)

        session_id = num_sessions_1

        session = self.gofp.get_session(session_id)

        (
            nft_address,
            payment_address,
            payment_amount,
            is_active,
            is_choosing_active,
            uri,
            stages,
            is_forgiving,
        ) = session

        self.assertEqual(nft_address, self.nft.address)
        self.assertEqual(payment_address, self.payment_token.address)
        self.assertEqual(payment_amount, expected_payment_amount)
        self.assertTrue(is_active)
        self.assertEqual(uri, expected_uri)
        self.assertEqual(stages, expected_stages)
        self.assertEqual(is_forgiving, False)
        self.assertEqual(is_choosing_active, True)

    def test_create_session_then_get_session_inactive(self):
        num_sessions_0 = self.gofp.num_sessions()

        expected_payment_amount = 43
        expected_uri = (
            "https://example.com/test_create_session_then_get_session_inactive.json"
        )
        expected_stages = (5, 5, 3)
        expected_is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            expected_payment_amount,
            expected_is_active,
            expected_uri,
            expected_stages,
            False,
            {"from": self.game_master},
        )

        num_sessions_1 = self.gofp.num_sessions()
        self.assertEqual(num_sessions_1, num_sessions_0 + 1)

        session_id = num_sessions_1

        session = self.gofp.get_session(session_id)

        (
            nft_address,
            payment_address,
            payment_amount,
            is_active,
            is_choosing_active,
            uri,
            stages,
            is_forgiving,
        ) = session

        self.assertEqual(nft_address, self.nft.address)
        self.assertEqual(payment_address, self.payment_token.address)
        self.assertEqual(payment_amount, expected_payment_amount)
        self.assertFalse(is_active)
        self.assertEqual(uri, expected_uri)
        self.assertEqual(stages, expected_stages)
        self.assertEqual(is_forgiving, False)
        self.assertEqual(is_choosing_active, True)

    def test_create_forgiving_session_then_get_session_active(self):
        num_sessions_0 = self.gofp.num_sessions()

        expected_payment_amount = 42
        expected_uri = "https://example.com/test_create_forgiving_session_then_get_session_active.json"
        expected_stages = (5, 5, 3, 3, 2)
        expected_is_active = True
        expected_is_forgiving = True

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            expected_payment_amount,
            expected_is_active,
            expected_uri,
            expected_stages,
            expected_is_forgiving,
            {"from": self.game_master},
        )

        num_sessions_1 = self.gofp.num_sessions()
        self.assertEqual(num_sessions_1, num_sessions_0 + 1)

        session_id = num_sessions_1

        session = self.gofp.get_session(session_id)

        (
            nft_address,
            payment_address,
            payment_amount,
            is_active,
            is_choosing_active,
            uri,
            stages,
            is_forgiving,
        ) = session

        self.assertEqual(nft_address, self.nft.address)
        self.assertEqual(payment_address, self.payment_token.address)
        self.assertEqual(payment_amount, expected_payment_amount)
        self.assertTrue(is_active)
        self.assertEqual(uri, expected_uri)
        self.assertEqual(stages, expected_stages)
        self.assertEqual(is_forgiving, expected_is_forgiving)
        self.assertEqual(is_choosing_active, True)

    def test_create_free_session(self):
        num_sessions_0 = self.gofp.num_sessions()

        expected_uri = "https://example.com/test_create_free_session.json"
        expected_stages = (5, 5, 3)
        expected_is_active = False

        with self.assertRaises(VirtualMachineError):
            self.gofp.create_session(
                self.nft.address,
                ZERO_ADDRESS,
                1,
                expected_is_active,
                expected_uri,
                expected_stages,
                False,
                {"from": self.game_master},
            )

        self.gofp.create_session(
            self.nft.address,
            ZERO_ADDRESS,
            0,
            expected_is_active,
            expected_uri,
            expected_stages,
            False,
            {"from": self.game_master},
        )

        num_sessions_1 = self.gofp.num_sessions()
        self.assertEqual(num_sessions_1, num_sessions_0 + 1)

        session_id = num_sessions_1

        session = self.gofp.get_session(session_id)

        (
            nft_address,
            payment_address,
            payment_amount,
            is_active,
            is_choosing_active,
            uri,
            stages,
            is_forgiving,
        ) = session

        self.assertEqual(nft_address, self.nft.address)
        self.assertEqual(payment_address, ZERO_ADDRESS)
        self.assertEqual(payment_amount, 0)
        self.assertFalse(is_active)
        self.assertEqual(uri, expected_uri)
        self.assertEqual(stages, expected_stages)
        self.assertEqual(is_forgiving, False)
        self.assertEqual(is_choosing_active, True)

    def test_cannot_create_session_as_player(self):
        num_sessions_0 = self.gofp.num_sessions()

        failed_payment_amount = 44
        failed_uri = "https://example.com/test_cannot_create_session_as_player.json"
        failed_stages = (5, 5)
        failed_is_active = True

        with self.assertRaises(VirtualMachineError):
            self.gofp.create_session(
                self.nft.address,
                self.payment_token.address,
                failed_payment_amount,
                failed_is_active,
                failed_uri,
                failed_stages,
                False,
                {"from": self.player},
            )

        num_sessions_1 = self.gofp.num_sessions()
        self.assertEqual(num_sessions_1, num_sessions_0)

    def test_cannot_create_session_as_contract_owner_who_is_not_game_master(self):
        num_sessions_0 = self.gofp.num_sessions()

        failed_payment_amount = 44
        failed_uri = "https://example.com/test_cannot_create_session_as_contract_owner_who_is_not_game_master.json"
        failed_stages = (5, 5)
        failed_is_active = True

        with self.assertRaises(VirtualMachineError):
            self.gofp.create_session(
                self.nft.address,
                self.payment_token.address,
                failed_payment_amount,
                failed_is_active,
                failed_uri,
                failed_stages,
                False,
                {"from": self.owner},
            )

        num_sessions_1 = self.gofp.num_sessions()
        self.assertEqual(num_sessions_1, num_sessions_0)

    def test_create_session_fires_events(self):
        expected_payment_amount = 60
        expected_uri = "https://example.com/test_create_session_fires_events.json"
        expected_stages = (5,)
        expected_is_active = True
        expected_is_forgiving = True

        tx_receipt = self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            expected_payment_amount,
            expected_is_active,
            expected_uri,
            expected_stages,
            expected_is_forgiving,
            {"from": self.game_master},
        )

        session_created_events = _fetch_events_chunk(
            web3_client,
            SESSION_CREATED_EVENT_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )

        self.assertEqual(len(session_created_events), 1)

        self.assertEqual(
            session_created_events[0]["args"]["sessionId"], self.gofp.num_sessions()
        )
        self.assertEqual(
            session_created_events[0]["args"]["playerTokenAddress"], self.nft.address
        )
        self.assertEqual(
            session_created_events[0]["args"]["paymentTokenAddress"],
            self.payment_token.address,
        )
        self.assertEqual(
            session_created_events[0]["args"]["paymentAmount"], expected_payment_amount
        )
        self.assertEqual(session_created_events[0]["args"]["uri"], expected_uri)
        self.assertEqual(
            session_created_events[0]["args"]["active"], expected_is_active
        )
        self.assertEqual(
            session_created_events[0]["args"]["isForgiving"], expected_is_forgiving
        )

        session_activated_events = _fetch_events_chunk(
            web3_client,
            SESSION_ACTIVATED_EVENT_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )
        self.assertEqual(len(session_activated_events), 1)
        self.assertEqual(
            session_activated_events[0]["args"]["sessionId"], self.gofp.num_sessions()
        )
        self.assertEqual(
            session_activated_events[0]["args"]["active"], expected_is_active
        )

        session_choosing_activated_events = _fetch_events_chunk(
            web3_client,
            SESSION_CHOOSING_ACTIVATED_EVENT_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )
        self.assertEqual(len(session_choosing_activated_events), 1)
        self.assertEqual(
            session_choosing_activated_events[0]["args"]["sessionId"],
            self.gofp.num_sessions(),
        )
        self.assertEqual(
            session_choosing_activated_events[0]["args"]["isChoosingActive"], True
        )

        session_uri_changed_events = _fetch_events_chunk(
            web3_client,
            SESSION_URI_CHANGED_EVENT_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )
        self.assertEqual(len(session_uri_changed_events), 1)
        self.assertEqual(
            session_uri_changed_events[0]["args"]["sessionId"], self.gofp.num_sessions()
        )
        self.assertEqual(session_uri_changed_events[0]["args"]["uri"], expected_uri)

    def test_can_change_session_info_as_game_master_and_not_as_random_person(self):
        """
        Tests that game masters can correctly modify the following attributes of a session:
        - isActive
        - isChoosingActive
        - uri

        Also tests that non game masters *cannot* call these methods.

        Also tests that the appropriate events are fired when the methods are called.
        """
        payment_amount = 130
        uri = "https://example.com/test_can_change_session_info_as_game_master_and_not_as_random_person.json"
        stages = (5, 5, 3)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # We create a second session to ensure that the information modified for the first session is not
        # being modified on the second session instead. This was a bug in a development version of the
        # contract.
        other_stages = (1, 1, 1)
        other_active = False
        other_uri = "https://example.com/lol.json"
        self.gofp.create_session(
            self.nft.address,
            ZERO_ADDRESS,
            0,
            other_active,
            other_uri,
            other_stages,
            False,
            {"from": self.game_master},
        )

        _, _, _, is_active_0, is_choosing_active_0, uri_0, _, _ = self.gofp.get_session(
            session_id
        )
        self.assertFalse(is_active_0)
        self.assertTrue(is_choosing_active_0)
        self.assertEqual(uri_0, uri)

        # Sanity check: random person should not be game master:
        self.assertEqual(
            self.terminus.balance_of(self.random_person.address, self.admin_pool_id), 0
        )

        # setSessionActive tests
        session_active_tx_receipt_0 = self.gofp.set_session_active(
            session_id, True, {"from": self.game_master}
        )

        _, _, _, is_active_1, _, _, _, _ = self.gofp.get_session(session_id)
        self.assertTrue(is_active_1)

        session_activated_events_0 = _fetch_events_chunk(
            web3_client,
            SESSION_ACTIVATED_EVENT_ABI,
            from_block=session_active_tx_receipt_0.block_number,
            to_block=session_active_tx_receipt_0.block_number,
        )
        self.assertEqual(len(session_activated_events_0), 1)
        self.assertEqual(session_activated_events_0[0]["args"]["sessionId"], session_id)
        self.assertEqual(session_activated_events_0[0]["args"]["active"], is_active_1)

        session_active_tx_receipt_1 = self.gofp.set_session_active(
            session_id, False, {"from": self.game_master}
        )

        _, _, _, is_active_2, _, _, _, _ = self.gofp.get_session(session_id)
        self.assertFalse(is_active_2)

        session_activated_events_1 = _fetch_events_chunk(
            web3_client,
            SESSION_ACTIVATED_EVENT_ABI,
            from_block=session_active_tx_receipt_1.block_number,
            to_block=session_active_tx_receipt_1.block_number,
        )
        self.assertEqual(len(session_activated_events_1), 1)
        self.assertEqual(session_activated_events_1[0]["args"]["sessionId"], session_id)
        self.assertEqual(session_activated_events_1[0]["args"]["active"], is_active_2)

        session_active_tx_receipt_2 = self.gofp.set_session_active(
            session_id, False, {"from": self.game_master}
        )

        _, _, _, is_active_3, _, _, _, _ = self.gofp.get_session(session_id)
        self.assertFalse(is_active_3)

        session_activated_events_2 = _fetch_events_chunk(
            web3_client,
            SESSION_ACTIVATED_EVENT_ABI,
            from_block=session_active_tx_receipt_2.block_number,
            to_block=session_active_tx_receipt_2.block_number,
        )
        self.assertEqual(len(session_activated_events_2), 1)
        self.assertEqual(session_activated_events_2[0]["args"]["sessionId"], session_id)
        self.assertEqual(session_activated_events_2[0]["args"]["active"], is_active_3)

        with self.assertRaises(VirtualMachineError):
            self.gofp.set_session_active(session_id, True, {"from": self.random_person})

        _, _, _, is_active_4, _, _, _, _ = self.gofp.get_session(session_id)
        self.assertEqual(is_active_4, is_active_3)

        # setSessionChoosingActive tests
        session_choosing_active_tx_receipt_0 = self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )

        _, _, _, _, is_choosing_active_1, _, _, _ = self.gofp.get_session(session_id)
        self.assertFalse(is_choosing_active_1)

        session_choosing_activated_events_0 = _fetch_events_chunk(
            web3_client,
            SESSION_CHOOSING_ACTIVATED_EVENT_ABI,
            from_block=session_choosing_active_tx_receipt_0.block_number,
            to_block=session_choosing_active_tx_receipt_0.block_number,
        )
        self.assertEqual(len(session_choosing_activated_events_0), 1)
        self.assertEqual(
            session_choosing_activated_events_0[0]["args"]["sessionId"], session_id
        )
        self.assertEqual(
            session_choosing_activated_events_0[0]["args"]["isChoosingActive"],
            is_choosing_active_1,
        )

        session_choosing_active_tx_receipt_1 = self.gofp.set_session_choosing_active(
            session_id, True, {"from": self.game_master}
        )

        _, _, _, _, is_choosing_active_2, _, _, _ = self.gofp.get_session(session_id)
        self.assertTrue(is_choosing_active_2)

        session_choosing_activated_events_1 = _fetch_events_chunk(
            web3_client,
            SESSION_CHOOSING_ACTIVATED_EVENT_ABI,
            from_block=session_choosing_active_tx_receipt_1.block_number,
            to_block=session_choosing_active_tx_receipt_1.block_number,
        )
        self.assertEqual(len(session_choosing_activated_events_1), 1)
        self.assertEqual(
            session_choosing_activated_events_1[0]["args"]["sessionId"], session_id
        )
        self.assertEqual(
            session_choosing_activated_events_1[0]["args"]["isChoosingActive"],
            is_choosing_active_2,
        )

        session_choosing_active_tx_receipt_2 = self.gofp.set_session_choosing_active(
            session_id, True, {"from": self.game_master}
        )

        _, _, _, _, is_choosing_active_3, _, _, _ = self.gofp.get_session(session_id)
        self.assertTrue(is_choosing_active_3)

        session_choosing_activated_events_2 = _fetch_events_chunk(
            web3_client,
            SESSION_CHOOSING_ACTIVATED_EVENT_ABI,
            from_block=session_choosing_active_tx_receipt_2.block_number,
            to_block=session_choosing_active_tx_receipt_2.block_number,
        )
        self.assertEqual(len(session_choosing_activated_events_2), 1)
        self.assertEqual(
            session_choosing_activated_events_2[0]["args"]["sessionId"], session_id
        )
        self.assertEqual(
            session_choosing_activated_events_2[0]["args"]["isChoosingActive"],
            is_choosing_active_3,
        )

        with self.assertRaises(VirtualMachineError):
            self.gofp.set_session_choosing_active(
                session_id, not is_choosing_active_3, {"from": self.random_person}
            )

        _, _, _, _, is_choosing_active_4, _, _, _ = self.gofp.get_session(session_id)
        self.assertEqual(is_choosing_active_4, is_choosing_active_3)

        # setSessionUri tests
        new_uri_0 = "https://example.com/new_uri_0.json"
        session_uri_changed_tx_receipt_0 = self.gofp.set_session_uri(
            session_id, new_uri_0, {"from": self.game_master}
        )

        _, _, _, _, _, uri_1, _, _ = self.gofp.get_session(session_id)
        self.assertEqual(uri_1, new_uri_0)

        session_uri_changed_events_0 = _fetch_events_chunk(
            web3_client,
            SESSION_URI_CHANGED_EVENT_ABI,
            from_block=session_uri_changed_tx_receipt_0.block_number,
            to_block=session_uri_changed_tx_receipt_0.block_number,
        )
        self.assertEqual(len(session_uri_changed_events_0), 1)
        self.assertEqual(
            session_uri_changed_events_0[0]["args"]["sessionId"], session_id
        )
        self.assertEqual(
            session_uri_changed_events_0[0]["args"]["uri"],
            uri_1,
        )

        new_uri_1 = "https://example.com/new_uri_1.json"
        session_uri_changed_tx_receipt_1 = self.gofp.set_session_uri(
            session_id, new_uri_1, {"from": self.game_master}
        )

        _, _, _, _, _, uri_2, _, _ = self.gofp.get_session(session_id)
        self.assertEqual(uri_2, new_uri_1)

        session_uri_changed_events_1 = _fetch_events_chunk(
            web3_client,
            SESSION_URI_CHANGED_EVENT_ABI,
            from_block=session_uri_changed_tx_receipt_1.block_number,
            to_block=session_uri_changed_tx_receipt_1.block_number,
        )
        self.assertEqual(len(session_uri_changed_events_1), 1)
        self.assertEqual(
            session_uri_changed_events_1[0]["args"]["sessionId"], session_id
        )
        self.assertEqual(
            session_uri_changed_events_1[0]["args"]["uri"],
            uri_2,
        )

        new_uri_2 = "https://example.com/new_uri_2.json"
        session_uri_changed_tx_receipt_2 = self.gofp.set_session_uri(
            session_id, new_uri_2, {"from": self.game_master}
        )

        _, _, _, _, _, uri_3, _, _ = self.gofp.get_session(session_id)
        self.assertEqual(uri_3, new_uri_2)

        session_uri_changed_events_2 = _fetch_events_chunk(
            web3_client,
            SESSION_URI_CHANGED_EVENT_ABI,
            from_block=session_uri_changed_tx_receipt_2.block_number,
            to_block=session_uri_changed_tx_receipt_2.block_number,
        )
        self.assertEqual(len(session_uri_changed_events_2), 1)
        self.assertEqual(
            session_uri_changed_events_2[0]["args"]["sessionId"], session_id
        )
        self.assertEqual(
            session_uri_changed_events_2[0]["args"]["uri"],
            uri_3,
        )

        with self.assertRaises(VirtualMachineError):
            self.gofp.set_session_uri(
                session_id, f"{uri_3}/{uri_3}", {"from": self.random_person}
            )

        _, _, _, _, _, uri_4, _, _ = self.gofp.get_session(session_id)
        self.assertEqual(uri_4, uri_3)

        # Check that the next session we created was not modified
        (
            _,
            _,
            _,
            other_session_active_final,
            other_session_choosing_active_final,
            other_session_uri_final,
            _,
            _,
        ) = self.gofp.get_session(session_id + 1)
        self.assertEqual(other_session_active_final, other_active)
        self.assertTrue(other_session_choosing_active_final)
        self.assertEqual(other_session_uri_final, other_uri)

    def test_game_master_can_register_path(self):
        payment_amount = 131
        uri = "https://example.com/test_game_master_can_register_path.json"
        stages = (5, 5, 3)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )
        self.gofp.set_correct_path_for_stage(
            session_id, 1, 1, False, {"from": self.game_master}
        )

        paths_0 = (
            self.gofp.get_correct_path_for_stage(session_id, 1),
            self.gofp.get_correct_path_for_stage(session_id, 2),
            self.gofp.get_correct_path_for_stage(session_id, 3),
        )
        self.assertEqual(paths_0, (1, 0, 0))

        self.gofp.set_correct_path_for_stage(
            session_id, 2, 5, False, {"from": self.game_master}
        )

        paths_1 = (
            self.gofp.get_correct_path_for_stage(session_id, 1),
            self.gofp.get_correct_path_for_stage(session_id, 2),
            self.gofp.get_correct_path_for_stage(session_id, 3),
        )
        self.assertEqual(paths_1, (1, 5, 0))

        self.gofp.set_correct_path_for_stage(
            session_id, 3, 3, False, {"from": self.game_master}
        )
        paths_2 = (
            self.gofp.get_correct_path_for_stage(session_id, 1),
            self.gofp.get_correct_path_for_stage(session_id, 2),
            self.gofp.get_correct_path_for_stage(session_id, 3),
        )
        self.assertEqual(paths_2, (1, 5, 3))

    def test_non_game_master_cannot_register_path(self):
        payment_amount = 131
        uri = "https://example.com/test_non_game_master_cannot_register_path.json"
        stages = (5, 5, 3)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        with self.assertRaises(VirtualMachineError):
            self.gofp.set_correct_path_for_stage(
                session_id, 1, 1, True, {"from": self.player}
            )
        paths_0 = (
            self.gofp.get_correct_path_for_stage(session_id, 1),
            self.gofp.get_correct_path_for_stage(session_id, 2),
            self.gofp.get_correct_path_for_stage(session_id, 3),
        )
        self.assertEqual(paths_0, (0, 0, 0))

    def test_game_master_cannot_register_invalid_path(self):
        payment_amount = 131
        uri = "https://example.com/test_game_master_cannot_register_invalid_path.json"
        stages = (5, 5, 3)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # Invalid session
        with self.assertRaises(VirtualMachineError):
            self.gofp.set_correct_path_for_stage(
                session_id + 1, 1, 5, True, {"from": self.game_master}
            )
        paths_0 = (
            self.gofp.get_correct_path_for_stage(session_id, 1),
            self.gofp.get_correct_path_for_stage(session_id, 2),
            self.gofp.get_correct_path_for_stage(session_id, 3),
        )
        self.assertEqual(paths_0, (0, 0, 0))

        # Invalid stage - one greater than number of stages
        with self.assertRaises(VirtualMachineError):
            self.gofp.set_correct_path_for_stage(
                session_id, 4, 1, True, {"from": self.game_master}
            )
        paths_1 = (
            self.gofp.get_correct_path_for_stage(session_id, 1),
            self.gofp.get_correct_path_for_stage(session_id, 2),
            self.gofp.get_correct_path_for_stage(session_id, 3),
        )
        self.assertEqual(paths_1, (0, 0, 0))

        # Invalid stage - stage 0
        with self.assertRaises(VirtualMachineError):
            self.gofp.set_correct_path_for_stage(
                session_id, 0, 1, True, {"from": self.game_master}
            )

        # Path must be >= 1
        with self.assertRaises(VirtualMachineError):
            self.gofp.set_correct_path_for_stage(
                session_id, 1, 0, True, {"from": self.game_master}
            )
        paths_2 = (
            self.gofp.get_correct_path_for_stage(session_id, 1),
            self.gofp.get_correct_path_for_stage(session_id, 2),
            self.gofp.get_correct_path_for_stage(session_id, 3),
        )
        self.assertEqual(paths_2, (0, 0, 0))

        # Path must be <= number of choices for the given stage
        with self.assertRaises(VirtualMachineError):
            self.gofp.set_correct_path_for_stage(
                session_id, 1, 6, True, {"from": self.game_master}
            )
        paths_3 = (
            self.gofp.get_correct_path_for_stage(session_id, 1),
            self.gofp.get_correct_path_for_stage(session_id, 2),
            self.gofp.get_correct_path_for_stage(session_id, 3),
        )
        self.assertEqual(paths_3, (0, 0, 0))

    def test_game_master_cannot_register_path_multiple_times_for_same_stage(self):
        payment_amount = 131
        uri = "https://example.com/test_game_master_cannot_register_path_multiple_times_for_same_stage.json"
        stages = (5, 5, 3)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )

        self.gofp.set_correct_path_for_stage(
            session_id, 1, 5, False, {"from": self.game_master}
        )
        paths_0 = (
            self.gofp.get_correct_path_for_stage(session_id, 1),
            self.gofp.get_correct_path_for_stage(session_id, 2),
            self.gofp.get_correct_path_for_stage(session_id, 3),
        )
        self.assertEqual(paths_0, (5, 0, 0))

        with self.assertRaises(VirtualMachineError):
            self.gofp.set_correct_path_for_stage(
                session_id, 1, 4, False, {"from": self.game_master}
            )
        paths_1 = (
            self.gofp.get_correct_path_for_stage(session_id, 1),
            self.gofp.get_correct_path_for_stage(session_id, 2),
            self.gofp.get_correct_path_for_stage(session_id, 3),
        )
        self.assertEqual(paths_1, (5, 0, 0))

        self.gofp.set_correct_path_for_stage(
            session_id, 2, 3, False, {"from": self.game_master}
        )
        paths_2 = (
            self.gofp.get_correct_path_for_stage(session_id, 1),
            self.gofp.get_correct_path_for_stage(session_id, 2),
            self.gofp.get_correct_path_for_stage(session_id, 3),
        )
        self.assertEqual(paths_2, (5, 3, 0))

    def test_register_path_fires_event(self):
        payment_amount = 131
        uri = "https://example.com/test_register_path_fires_event.json"
        stages = (5, 5, 3)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )

        tx_receipt = self.gofp.set_correct_path_for_stage(
            session_id, 1, 5, False, {"from": self.game_master}
        )
        events = _fetch_events_chunk(
            web3_client,
            PATH_REGISTERED_EVENT_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )

        self.assertEqual(len(events), 1)

        self.assertEqual(events[0]["args"]["sessionId"], self.gofp.num_sessions())
        self.assertEqual(events[0]["args"]["stage"], 1)
        self.assertEqual(events[0]["args"]["path"], 5)

    def test_set_and_get_stage_rewards(self):
        """
        Tests administrators' ability to set rewards for the stages in a session. Also tests anyone's
        ability to view the rewards for a given stage in a given session.

        Test actions:
        1. Create active session
        2. Check rewards have default values
        3. Attempt to set rewards on active session should fail
        4. Check rewards still have default values
        5. Make session inactive
        6. Set rewards for all but the first stage
        7. Check that rewards were correctly set
        8. Check that the extend StageRewardChanged events are fired
        """
        payment_amount = 132
        uri = "https://example.com/test_set_and_get_stage_rewards.json"
        stages = (5, 5, 3, 3, 2)
        is_active = True

        # Rewards should be associated with all but the first stage in the session.
        stages_with_rewards = list(range(2, len(stages) + 1))

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        for i in range(1, len(stages) + 1):
            reward = self.gofp.get_stage_reward(session_id, i)
            self.assertEqual(reward, (ZERO_ADDRESS, 0, 0))

        with self.assertRaises(VirtualMachineError):
            self.gofp.set_stage_rewards(
                session_id,
                stages_with_rewards,
                [self.terminus.address for _ in stages_with_rewards],
                [self.reward_pool_id for _ in stages_with_rewards],
                [i + 1 for i, _ in enumerate(stages_with_rewards)],
                {"from": self.game_master},
            )

        for i in range(1, len(stages) + 1):
            reward = self.gofp.get_stage_reward(session_id, i)
            self.assertEqual(reward, (ZERO_ADDRESS, 0, 0))

        self.gofp.set_session_active(session_id, False, {"from": self.game_master})

        tx_receipt = self.gofp.set_stage_rewards(
            session_id,
            stages_with_rewards,
            [self.terminus.address for _ in stages_with_rewards],
            [self.reward_pool_id for _ in stages_with_rewards],
            [i + 1 for i, _ in enumerate(stages_with_rewards)],
            {"from": self.game_master},
        )

        reward = self.gofp.get_stage_reward(session_id, 1)
        self.assertEqual(reward, (ZERO_ADDRESS, 0, 0))

        for i in range(2, len(stages) + 1):
            reward = self.gofp.get_stage_reward(session_id, i)
            self.assertEqual(
                reward, (self.terminus.address, self.reward_pool_id, i - 1)
            )

        events = _fetch_events_chunk(
            web3_client,
            STAGE_REWARD_CHANGED_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )

        self.assertEqual(len(events), len(stages_with_rewards))
        self.assertListEqual(
            [event["args"]["sessionId"] for event in events],
            [session_id for _ in stages_with_rewards],
        )
        self.assertListEqual(
            [event["args"]["stage"] for event in events],
            [stage for stage in stages_with_rewards],
        )
        self.assertListEqual(
            [event["args"]["terminusAddress"] for event in events],
            [self.terminus.address for _ in stages_with_rewards],
        )
        self.assertListEqual(
            [event["args"]["terminusPoolId"] for event in events],
            [self.reward_pool_id for _ in stages_with_rewards],
        )
        self.assertListEqual(
            [event["args"]["rewardAmount"] for event in events],
            [i + 1 for i, _ in enumerate(stages_with_rewards)],
        )

    def test_non_game_master_cannot_set_stage_rewards(self):
        """
        Tests that non game master accounts cannot set stage rewards on an inactive session.

        Test actions:
        1. Create inactive session
        2. Check that player is not a game master (i.e. does not have game master badge)
        3. Attempt by player to set rewards on active session should fail
        4. Check rewards still have default values
        """
        payment_amount = 133
        uri = "https://example.com/test_non_game_master_cannot_set_stage_rewards.json"
        stages = (5, 5, 3, 3, 2)
        is_active = False

        # Rewards should be associated with all but the first stage in the session.
        stages_with_rewards = list(range(2, len(stages) + 1))

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        self.assertEqual(
            self.terminus.balance_of(self.player.address, self.admin_pool_id), 0
        )

        with self.assertRaises(VirtualMachineError):
            self.gofp.set_stage_rewards(
                session_id,
                stages_with_rewards,
                [self.terminus.address for _ in stages_with_rewards],
                [self.reward_pool_id for _ in stages_with_rewards],
                [i + 1 for i, _ in enumerate(stages_with_rewards)],
                {"from": self.player},
            )

        for i in range(1, len(stages) + 1):
            reward = self.gofp.get_stage_reward(session_id, i)
            self.assertEqual(reward, (ZERO_ADDRESS, 0, 0))

    def test_setting_same_stage_reward_twice_overwrites_first_value(self):
        """
        Tests administrators' ability to set rewards for the stages in a session. Also tests anyone's
        ability to view the rewards for a given stage in a given session.

        Test actions:
        1. Create inactive session
        2. Check rewards have default values
        3. Set stage rewards with a duplicate stage
        7. Check that rewards were correctly set (stage reward set twice should use second value)
        """
        payment_amount = 132
        uri = "https://example.com/test_setting_same_stage_reward_twice_overwrites_first_value.json"
        stages = (5, 5, 3, 3, 2)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        for i in range(1, len(stages) + 1):
            reward = self.gofp.get_stage_reward(session_id, i)
            self.assertEqual(reward, (ZERO_ADDRESS, 0, 0))

        stages_with_rewards = [1, 2, 3, 4, 5, 1]
        stage_rewards = list(range(1, len(stages_with_rewards) + 1))

        self.gofp.set_stage_rewards(
            session_id,
            stages_with_rewards,
            [self.terminus.address for _ in stages_with_rewards],
            [self.reward_pool_id for _ in stages_with_rewards],
            stage_rewards,
            {"from": self.game_master},
        )

        for i in range(2, len(stages) + 1):
            reward = self.gofp.get_stage_reward(session_id, i)
            self.assertEqual(reward, (self.terminus.address, self.reward_pool_id, i))

        first_stage_reward = self.gofp.get_stage_reward(session_id, 1)
        self.assertEqual(
            first_stage_reward,
            (
                self.terminus.address,
                self.reward_pool_id,
                stage_rewards[len(stage_rewards) - 1],
            ),
        )

    def test_set_and_get_path_rewards(self):
        """
        Tests administrators' ability to set rewards for the paths in a session. Also tests anyone's
        ability to view the rewards for a given path in a given stage in a given session.

        Test actions:
        1. Create active session
        2. Check rewards have default values
        3. Attempt to set rewards on active session should fail
        4. Check rewards still have default values
        5. Make session inactive
        6. Set rewards for all but the first stage
        7. Check that rewards were correctly set
        8. Check that the extend StageRewardChanged events are fired
        """
        payment_amount = 132
        uri = "https://example.com/test_set_and_get_path_rewards.json"
        stages = (5, 5, 3, 3, 2)
        is_active = True

        stages_with_rewards = [2, 2, 3, 4, 5, 2]
        paths_with_rewards = [2, 4, 1, 2, 1, 2]

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        for i in range(1, len(stages) + 1):
            for j in range(1, stages[i - 1]):
                reward = self.gofp.get_path_reward(session_id, i, j)
                self.assertEqual(reward, (ZERO_ADDRESS, 0, 0))

        with self.assertRaises(VirtualMachineError):
            self.gofp.set_path_rewards(
                session_id,
                stages_with_rewards,
                paths_with_rewards,
                [self.terminus.address for _ in paths_with_rewards],
                [self.reward_pool_id for _ in paths_with_rewards],
                [
                    (2**stage) * (3**path)
                    for stage, path in zip(stages_with_rewards, paths_with_rewards)
                ],
                {"from": self.game_master},
            )

        for i in range(1, len(stages) + 1):
            for j in range(1, stages[i - 1]):
                reward = self.gofp.get_path_reward(session_id, i, j)
                self.assertEqual(reward, (ZERO_ADDRESS, 0, 0))

        self.gofp.set_session_active(session_id, False, {"from": self.game_master})

        tx_receipt = self.gofp.set_path_rewards(
            session_id,
            stages_with_rewards,
            paths_with_rewards,
            [self.terminus.address for _ in paths_with_rewards],
            [self.reward_pool_id for _ in paths_with_rewards],
            [
                (2**stage) * (3**path)
                for stage, path in zip(stages_with_rewards, paths_with_rewards)
            ],
            {"from": self.game_master},
        )

        for stage, path in zip(stages_with_rewards, paths_with_rewards):
            reward = self.gofp.get_path_reward(session_id, stage, path)
            self.assertEqual(
                reward,
                (
                    self.terminus.address,
                    self.reward_pool_id,
                    (2**stage) * (3**path),
                ),
            )

        events = _fetch_events_chunk(
            web3_client,
            PATH_REWARD_CHANGED_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )

        self.assertEqual(len(events), len(paths_with_rewards))
        self.assertListEqual(
            [event["args"]["sessionId"] for event in events],
            [session_id for _ in paths_with_rewards],
        )
        self.assertListEqual(
            [event["args"]["stage"] for event in events],
            stages_with_rewards,
        )
        self.assertListEqual(
            [event["args"]["path"] for event in events],
            paths_with_rewards,
        )
        self.assertListEqual(
            [event["args"]["terminusAddress"] for event in events],
            [self.terminus.address for _ in paths_with_rewards],
        )
        self.assertListEqual(
            [event["args"]["terminusPoolId"] for event in events],
            [self.reward_pool_id for _ in paths_with_rewards],
        )
        self.assertListEqual(
            [event["args"]["rewardAmount"] for event in events],
            [
                (2**stage) * (3**path)
                for stage, path in zip(stages_with_rewards, paths_with_rewards)
            ],
        )

    def test_non_game_master_cannot_set_path_rewards(self):
        """
        Tests that non game master accounts cannot set path rewards on an inactive session.

        Test actions:
        1. Create inactive session
        2. Check that player is not a game master (i.e. does not have game master badge)
        3. Attempt by player to set rewards on active session should fail
        4. Check rewards still have default values
        """
        payment_amount = 133
        uri = "https://example.com/test_non_game_master_cannot_set_path_rewards.json"
        stages = (5, 5, 3, 3, 2)
        is_active = False

        stages_with_rewards = [2, 2, 3, 4, 5, 2]
        paths_with_rewards = [2, 4, 1, 2, 1, 2]

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        self.assertEqual(
            self.terminus.balance_of(self.player.address, self.admin_pool_id), 0
        )

        with self.assertRaises(VirtualMachineError):
            self.gofp.set_path_rewards(
                session_id,
                stages_with_rewards,
                paths_with_rewards,
                [self.terminus.address for _ in stages_with_rewards],
                [self.reward_pool_id for _ in stages_with_rewards],
                [
                    (2**stage) * (3**path)
                    for stage, path in zip(stages_with_rewards, paths_with_rewards)
                ],
                {"from": self.player},
            )

        for stage, path in zip(stages_with_rewards, paths_with_rewards):
            reward = self.gofp.get_path_reward(session_id, stage, path)
            self.assertEqual(reward, (ZERO_ADDRESS, 0, 0))

    def test_setting_same_path_reward_twice_overwrites_first_value(self):
        """
        Tests administrators' ability to set rewards for the stages in a session. Also tests anyone's
        ability to view the rewards for a given stage in a given session.

        Test actions:
        1. Create inactive session
        2. Check path rewards have default values
        3. Set path rewards with a duplicate path
        7. Check that rewards were correctly set (path reward set twice should use second value)
        """
        payment_amount = 132
        uri = "https://example.com/test_setting_same_path_reward_twice_overwrites_first_value.json"
        stages = (4, 1)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        for stage in range(1, len(stages) + 1):
            for path in range(1, stages[stage - 1] + 1):
                reward = self.gofp.get_path_reward(session_id, stage, path)
                self.assertEqual(reward, (ZERO_ADDRESS, 0, 0))

        stages_with_rewards = [1, 1, 1, 1, 2, 1]
        paths_with_rewards = [1, 2, 3, 4, 1, 3]
        # Reward is path number except for stage 1 path 3
        path_rewards = [1, 2, 3, 4, 1, 5]

        self.gofp.set_path_rewards(
            session_id,
            stages_with_rewards,
            paths_with_rewards,
            [self.terminus.address for _ in stages_with_rewards],
            [self.reward_pool_id for _ in stages_with_rewards],
            path_rewards,
            {"from": self.game_master},
        )

        for stage in range(1, len(stages) + 1):
            for path in range(1, stages[stage - 1] + 1):
                if stage != 1 or path != 3:
                    reward = self.gofp.get_path_reward(session_id, stage, path)
                    self.assertEqual(
                        reward,
                        (
                            self.terminus.address,
                            self.reward_pool_id,
                            path,
                        ),
                    )

        stage_1_path_3_reward = self.gofp.get_path_reward(session_id, 1, 3)
        self.assertEqual(
            stage_1_path_3_reward,
            (
                self.terminus.address,
                self.reward_pool_id,
                path_rewards[len(path_rewards) - 1],
            ),
        )


class TestPlayerFlow(GOFPTestCase):
    def test_player_can_stake_and_unstake_nfts(self):
        payment_amount = 131
        uri = "https://example.com/test_player_can_stake_and_unstake_nfts.json"
        stages = (5, 5, 3)
        is_active = True

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        num_nfts = 5
        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, len(token_ids) * payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        for token_id in token_ids:
            staked_session_id, owner = self.gofp.get_staked_token_info(
                self.nft.address, token_id
            )
            self.assertEqual(staked_session_id, 0)
            self.assertEqual(owner, ZERO_ADDRESS)

        num_staked_0 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_0 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_0 = self.nft.balance_of(self.gofp.address)

        self.gofp.stake_tokens_into_session(
            session_id, token_ids, {"from": self.player}
        )

        num_staked_1 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_1 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_1 = self.nft.balance_of(self.gofp.address)

        self.assertEqual(num_staked_1, num_staked_0 + len(token_ids))
        self.assertEqual(num_owned_by_player_1, num_owned_by_player_0 - len(token_ids))
        self.assertEqual(
            num_owned_by_contract_1, num_owned_by_contract_0 + len(token_ids)
        )

        for token_id in token_ids:
            staked_session_id, owner = self.gofp.get_staked_token_info(
                self.nft.address, token_id
            )
            self.assertEqual(staked_session_id, session_id)
            self.assertEqual(owner, self.player.address)

        for i, token_id in enumerate(token_ids):
            self.assertEqual(
                self.gofp.token_of_staker_in_session_by_index(
                    session_id,
                    self.player.address,
                    num_staked_1 - len(token_ids) + 1 + i,
                ),
                token_ids[i],
            )
            self.assertEqual(self.nft.owner_of(token_id), self.gofp.address)

        self.gofp.set_session_active(session_id, False, {"from": self.game_master})

        unstaked_token_ids = [token_ids[i] for i in range(1, len(token_ids) - 1)]

        self.gofp.unstake_tokens_from_session(
            session_id, unstaked_token_ids, {"from": self.player}
        )

        num_staked_2 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_2 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_2 = self.nft.balance_of(self.gofp.address)

        self.assertEqual(num_staked_2, num_staked_1 - len(unstaked_token_ids))
        self.assertEqual(
            num_owned_by_player_2, num_owned_by_player_1 + len(unstaked_token_ids)
        )
        self.assertEqual(
            num_owned_by_contract_2, num_owned_by_contract_1 - len(unstaked_token_ids)
        )

        staked_session_id, owner = self.gofp.get_staked_token_info(
            self.nft.address, token_ids[0]
        )
        self.assertEqual(staked_session_id, session_id)
        self.assertEqual(owner, self.player.address)

        staked_session_id, owner = self.gofp.get_staked_token_info(
            self.nft.address, token_ids[-1]
        )
        self.assertEqual(staked_session_id, session_id)
        self.assertEqual(owner, self.player.address)

        for token_id in unstaked_token_ids:
            staked_session_id, owner = self.gofp.get_staked_token_info(
                self.nft.address, token_id
            )
            self.assertEqual(staked_session_id, 0)
            self.assertEqual(owner, ZERO_ADDRESS)

        self.assertEqual(
            self.gofp.token_of_staker_in_session_by_index(
                session_id, self.player.address, num_staked_2 - 1
            ),
            token_ids[0],
        )
        self.assertEqual(
            self.gofp.token_of_staker_in_session_by_index(
                session_id, self.player.address, num_staked_2
            ),
            token_ids[-1],
        )
        for i in range(len(unstaked_token_ids)):
            self.assertEqual(
                self.gofp.token_of_staker_in_session_by_index(
                    session_id, self.player.address, num_staked_2 + i + 1
                ),
                0,
            )

        self.assertEqual(self.nft.owner_of(token_ids[0]), self.gofp.address)
        self.assertEqual(self.nft.owner_of(token_ids[-1]), self.gofp.address)
        for token_id in unstaked_token_ids:
            self.assertEqual(self.nft.owner_of(token_id), self.player.address)

    def test_player_can_stake_into_free_session(self):
        """
        Tests that, when a player stakes their tokens into a session which has no payment token set,
        the stake operation works without any ERC20 transfer events.
        """
        uri = "https://example.com/test_player_can_stake_into_free_session.json"
        stages = (5, 5, 3)
        is_active = True

        self.gofp.create_session(
            self.nft.address,
            ZERO_ADDRESS,
            0,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        num_nfts = 5
        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        for token_id in token_ids:
            staked_session_id, owner = self.gofp.get_staked_token_info(
                self.nft.address, token_id
            )
            self.assertEqual(staked_session_id, 0)
            self.assertEqual(owner, ZERO_ADDRESS)

        num_staked_0 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_0 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_0 = self.nft.balance_of(self.gofp.address)

        self.gofp.stake_tokens_into_session(
            session_id, token_ids, {"from": self.player}
        )

        num_staked_1 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_1 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_1 = self.nft.balance_of(self.gofp.address)

        self.assertEqual(num_staked_1, num_staked_0 + len(token_ids))
        self.assertEqual(num_owned_by_player_1, num_owned_by_player_0 - len(token_ids))
        self.assertEqual(
            num_owned_by_contract_1, num_owned_by_contract_0 + len(token_ids)
        )

        for token_id in token_ids:
            staked_session_id, owner = self.gofp.get_staked_token_info(
                self.nft.address, token_id
            )
            self.assertEqual(staked_session_id, session_id)
            self.assertEqual(owner, self.player.address)

        for i, token_id in enumerate(token_ids):
            self.assertEqual(
                self.gofp.token_of_staker_in_session_by_index(
                    session_id,
                    self.player.address,
                    num_staked_1 - len(token_ids) + 1 + i,
                ),
                token_ids[i],
            )
            self.assertEqual(self.nft.owner_of(token_id), self.gofp.address)

    def test_player_transfers_payment_token_on_staking(self):
        """
        Tests that, when a player stakes their tokens into a session which has payment token set,
        they also transfer the payment amount for each NFT they are staking.
        """
        payment_amount = 231
        uri = "https://example.com/test_player_transfers_payment_token_on_staking.json"
        stages = (5, 5, 3)
        is_active = True

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        num_nfts = 5
        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, len(token_ids) * payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        for token_id in token_ids:
            staked_session_id, owner = self.gofp.get_staked_token_info(
                self.nft.address, token_id
            )
            self.assertEqual(staked_session_id, 0)
            self.assertEqual(owner, ZERO_ADDRESS)

        num_staked_0 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_0 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_0 = self.nft.balance_of(self.gofp.address)
        player_payment_token_balance_0 = self.payment_token.balance_of(
            self.player.address
        )
        gofp_payment_token_balance_0 = self.payment_token.balance_of(self.gofp.address)

        self.gofp.stake_tokens_into_session(
            session_id, token_ids, {"from": self.player}
        )

        num_staked_1 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_1 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_1 = self.nft.balance_of(self.gofp.address)
        player_payment_token_balance_1 = self.payment_token.balance_of(
            self.player.address
        )
        gofp_payment_token_balance_1 = self.payment_token.balance_of(self.gofp.address)

        self.assertEqual(num_staked_1, num_staked_0 + len(token_ids))
        self.assertEqual(num_owned_by_player_1, num_owned_by_player_0 - len(token_ids))
        self.assertEqual(
            num_owned_by_contract_1, num_owned_by_contract_0 + len(token_ids)
        )
        self.assertEqual(
            player_payment_token_balance_1,
            player_payment_token_balance_0 - num_nfts * payment_amount,
        )
        self.assertEqual(
            gofp_payment_token_balance_1,
            gofp_payment_token_balance_0 + num_nfts * payment_amount,
        )

        for token_id in token_ids:
            staked_session_id, owner = self.gofp.get_staked_token_info(
                self.nft.address, token_id
            )
            self.assertEqual(staked_session_id, session_id)
            self.assertEqual(owner, self.player.address)

        for i, token_id in enumerate(token_ids):
            self.assertEqual(
                self.gofp.token_of_staker_in_session_by_index(
                    session_id,
                    self.player.address,
                    num_staked_1 - len(token_ids) + 1 + i,
                ),
                token_ids[i],
            )
            self.assertEqual(self.nft.owner_of(token_id), self.gofp.address)

    def test_random_person_cannot_stake_player_nfts(self):
        """
        Tests that a person cannot stake NFTs into a session which they do not own.
        Even if the person who owns those NFTs has given their approval to the Garden of Forking Paths
        contract.
        """
        payment_amount = 232
        uri = "https://example.com/test_random_person_cannot_stake_player_nfts.json"
        stages = (5, 5, 3)
        is_active = True

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        num_nfts = 5
        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.random_person.address,
            len(token_ids) * payment_amount,
            {"from": self.owner},
        )

        self.payment_token.approve(
            self.gofp.address, MAX_UINT, {"from": self.random_person}
        )
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})
        self.nft.set_approval_for_all(
            self.gofp.address, True, {"from": self.random_person}
        )

        num_staked_0 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_0 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_0 = self.nft.balance_of(self.gofp.address)
        player_payment_token_balance_0 = self.payment_token.balance_of(
            self.player.address
        )
        gofp_payment_token_balance_0 = self.payment_token.balance_of(self.gofp.address)
        random_person_payment_token_balance_0 = self.payment_token.balance_of(
            self.random_person.address
        )

        with self.assertRaises(VirtualMachineError):
            self.gofp.stake_tokens_into_session(
                session_id, token_ids, {"from": self.random_person}
            )

        num_staked_1 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_1 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_1 = self.nft.balance_of(self.gofp.address)
        player_payment_token_balance_1 = self.payment_token.balance_of(
            self.player.address
        )
        gofp_payment_token_balance_1 = self.payment_token.balance_of(self.gofp.address)
        random_person_payment_token_balance_1 = self.payment_token.balance_of(
            self.random_person.address
        )

        self.assertEqual(num_staked_1, num_staked_0)
        self.assertEqual(num_owned_by_player_1, num_owned_by_player_0)
        self.assertEqual(num_owned_by_contract_1, num_owned_by_contract_0)
        self.assertEqual(player_payment_token_balance_1, player_payment_token_balance_0)
        self.assertEqual(gofp_payment_token_balance_1, gofp_payment_token_balance_0)
        self.assertEqual(
            random_person_payment_token_balance_1, random_person_payment_token_balance_0
        )

    def test_random_person_cannot_unstake_nfts(self):
        payment_amount = 1337
        uri = "https://example.com/test_random_person_cannot_unstake_nfts.json"
        stages = (5, 5, 3)
        is_active = True

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        num_nfts = 5
        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, len(token_ids) * payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        self.gofp.stake_tokens_into_session(
            session_id, token_ids, {"from": self.player}
        )

        num_staked_0 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_0 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_0 = self.nft.balance_of(self.gofp.address)
        num_owned_by_random_0 = self.nft.balance_of(self.random_person.address)

        self.gofp.set_session_active(session_id, False, {"from": self.game_master})

        with self.assertRaises(VirtualMachineError):
            self.gofp.unstake_tokens_from_session(
                session_id, token_ids, {"from": self.random_person}
            )

        num_staked_1 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_1 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_1 = self.nft.balance_of(self.gofp.address)
        num_owned_by_random_1 = self.nft.balance_of(self.random_person.address)

        self.assertEqual(num_staked_1, num_staked_0)
        self.assertEqual(num_owned_by_player_1, num_owned_by_player_0)
        self.assertEqual(num_owned_by_contract_1, num_owned_by_contract_0)
        self.assertEqual(num_owned_by_random_1, num_owned_by_random_0)

        for token_id in token_ids:
            staked_session_id, staker = self.gofp.get_staked_token_info(
                self.nft.address, token_id
            )
            self.assertEqual(staked_session_id, session_id)
            self.assertEqual(staker, self.player.address)

    def test_player_cannot_stake_into_inactive_session(self):
        payment_amount = 133
        uri = "https://example.com/test_player_cannot_stake_into_inactive_session.json"
        stages = (5, 5, 3)
        is_active = True

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        self.gofp.set_session_active(session_id, False, {"from": self.game_master})

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        num_nfts = 5
        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, len(token_ids) * payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        for token_id in token_ids:
            staked_session_id, owner = self.gofp.get_staked_token_info(
                self.nft.address, token_id
            )
            self.assertEqual(staked_session_id, 0)
            self.assertEqual(owner, ZERO_ADDRESS)

        num_staked_0 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_0 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_0 = self.nft.balance_of(self.gofp.address)

        with self.assertRaises(VirtualMachineError):
            self.gofp.stake_tokens_into_session(
                session_id, token_ids, {"from": self.player}
            )

        num_staked_1 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_1 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_1 = self.nft.balance_of(self.gofp.address)

        self.assertEqual(num_staked_1, num_staked_0)
        self.assertEqual(num_owned_by_player_1, num_owned_by_player_0)
        self.assertEqual(num_owned_by_contract_1, num_owned_by_contract_0)

        for token_id in token_ids:
            staked_session_id, owner = self.gofp.get_staked_token_info(
                self.nft.address, token_id
            )
            self.assertEqual(staked_session_id, 0)
            self.assertEqual(owner, ZERO_ADDRESS)

        for i, token_id in enumerate(token_ids):
            self.assertEqual(self.nft.owner_of(token_id), self.player.address)

    def test_player_can_unstake_from_active_session(self):
        payment_amount = 135
        uri = "https://example.com/test_player_can_unstake_from_active_session.json"
        stages = (5, 5, 3)
        is_active = True

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        num_nfts = 5
        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, len(token_ids) * payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        for token_id in token_ids:
            staked_session_id, owner = self.gofp.get_staked_token_info(
                self.nft.address, token_id
            )
            self.assertEqual(staked_session_id, 0)
            self.assertEqual(owner, ZERO_ADDRESS)

        num_staked_0 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_0 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_0 = self.nft.balance_of(self.gofp.address)

        for token_id in token_ids:
            self.assertFalse(
                self.gofp.get_session_token_stake_guard(session_id, token_id)
            )

        self.gofp.stake_tokens_into_session(
            session_id, token_ids, {"from": self.player}
        )

        num_staked_1 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_1 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_1 = self.nft.balance_of(self.gofp.address)

        self.assertEqual(num_staked_1, num_staked_0 + len(token_ids))
        self.assertEqual(num_owned_by_player_1, num_owned_by_player_0 - len(token_ids))
        self.assertEqual(
            num_owned_by_contract_1, num_owned_by_contract_0 + len(token_ids)
        )

        for token_id in token_ids:
            staked_session_id, owner = self.gofp.get_staked_token_info(
                self.nft.address, token_id
            )
            self.assertEqual(staked_session_id, session_id)
            self.assertEqual(owner, self.player.address)

            self.assertTrue(
                self.gofp.get_session_token_stake_guard(session_id, token_id)
            )

        for i, token_id in enumerate(token_ids):
            self.assertEqual(
                self.gofp.token_of_staker_in_session_by_index(
                    session_id,
                    self.player.address,
                    num_staked_1 - len(token_ids) + 1 + i,
                ),
                token_ids[i],
            )
            self.assertEqual(self.nft.owner_of(token_id), self.gofp.address)

        self.gofp.set_session_active(session_id, True, {"from": self.game_master})

        unstaked_token_ids = [token_ids[i] for i in range(1, len(token_ids) - 1)]

        self.gofp.unstake_tokens_from_session(
            session_id, unstaked_token_ids, {"from": self.player}
        )

        num_staked_2 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_2 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_2 = self.nft.balance_of(self.gofp.address)

        self.assertEqual(num_staked_2, num_staked_1 - len(unstaked_token_ids))
        self.assertEqual(
            num_owned_by_player_2, num_owned_by_player_1 + len(unstaked_token_ids)
        )
        self.assertEqual(
            num_owned_by_contract_2, num_owned_by_contract_1 - len(unstaked_token_ids)
        )

        # First and last of the initially staked tokens should still be staked into the session in
        # that order
        staked_session_id, owner = self.gofp.get_staked_token_info(
            self.nft.address, token_ids[0]
        )
        self.assertEqual(staked_session_id, session_id)
        self.assertEqual(owner, self.player.address)
        self.assertTrue(self.gofp.get_session_token_stake_guard(session_id, token_id))
        self.assertEqual(
            self.gofp.token_of_staker_in_session_by_index(
                session_id,
                self.player.address,
                num_staked_0 + 1,
            ),
            token_ids[0],
        )
        self.assertEqual(self.nft.owner_of(token_ids[0]), self.gofp.address)

        staked_session_id, owner = self.gofp.get_staked_token_info(
            self.nft.address, token_ids[-1]
        )
        self.assertEqual(staked_session_id, session_id)
        self.assertEqual(owner, self.player.address)
        self.assertTrue(self.gofp.get_session_token_stake_guard(session_id, token_id))
        self.assertEqual(
            self.gofp.token_of_staker_in_session_by_index(
                session_id,
                self.player.address,
                num_staked_0 + 2,
            ),
            token_ids[-1],
        )
        self.assertEqual(self.nft.owner_of(token_ids[-1]), self.gofp.address)

        # Remaining tokens should be successfully unstaked
        for i, token_id in enumerate(unstaked_token_ids):
            staked_session_id, owner = self.gofp.get_staked_token_info(
                self.nft.address, token_id
            )
            self.assertEqual(staked_session_id, 0)
            self.assertEqual(owner, ZERO_ADDRESS)

            self.assertTrue(
                self.gofp.get_session_token_stake_guard(session_id, token_id)
            )

            self.assertEqual(
                self.gofp.token_of_staker_in_session_by_index(
                    session_id,
                    self.player.address,
                    len(token_ids) - len(unstaked_token_ids) + 1 + i,
                ),
                0,
            )
            self.assertEqual(self.nft.owner_of(token_id), self.player.address)

    def test_player_can_make_a_choice_with_staked_nfts_at_first_stage(self):
        payment_amount = 151
        uri = "https://example.com/test_player_can_make_a_choice_with_staked_nfts_at_first_stage.json"
        stages = (5, 5, 3)
        is_active = True

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        num_nfts = 5
        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, len(token_ids) * payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        self.gofp.stake_tokens_into_session(
            session_id, token_ids, {"from": self.player}
        )

        for token_id in token_ids:
            first_stage_path = self.gofp.get_path_choice(session_id, token_id, 1)
            self.assertEqual(first_stage_path, 0)

        tx_receipt = self.gofp.choose_current_stage_paths(
            session_id,
            token_ids,
            [token_id % stages[0] + 1 for token_id in token_ids],
            {"from": self.player},
        )

        for token_id in token_ids:
            first_stage_path = self.gofp.get_path_choice(session_id, token_id, 1)
            self.assertEqual(first_stage_path, token_id % stages[0] + 1)

        # Check if PathChosen events were fired for each token AND that they were fired in the expected
        # order. Events should be fired for each token in the order that the token was passed to the
        # chooseCurrentStagePaths method on the contract.
        events = _fetch_events_chunk(
            web3_client,
            PATH_CHOSEN_EVENT_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )

        self.assertEqual(len(events), len(token_ids))
        for i, event in enumerate(events):
            self.assertEqual(event["args"]["sessionId"], session_id)
            self.assertEqual(event["args"]["tokenId"], token_ids[i])
            self.assertEqual(event["args"]["stage"], 1)
            self.assertEqual(event["args"]["path"], token_ids[i] % stages[0] + 1)

    def test_player_cannot_make_a_choice_if_session_choosing_inactive(self):
        payment_amount = 153
        uri = "https://example.com/test_player_cannot_make_a_choice_if_session_choosing_inactive.json"
        stages = (5, 5, 3)
        is_active = True

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        num_nfts = 5
        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, len(token_ids) * payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        self.gofp.stake_tokens_into_session(
            session_id, token_ids, {"from": self.player}
        )

        for token_id in token_ids:
            first_stage_path = self.gofp.get_path_choice(session_id, token_id, 1)
            self.assertEqual(first_stage_path, 0)

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )

        with self.assertRaises(VirtualMachineError):
            self.gofp.choose_current_stage_paths(
                session_id,
                token_ids,
                [token_id % stages[0] + 1 for token_id in token_ids],
                {"from": self.player},
            )

        for token_id in token_ids:
            first_stage_path = self.gofp.get_path_choice(session_id, token_id, 1)
            self.assertEqual(first_stage_path, 0)

    def test_random_person_cannot_make_a_choice_with_player_nfts(self):
        payment_amount = 155
        uri = "https://example.com/test_random_person_cannot_make_a_choice_with_player_nfts.json"
        stages = (5, 5, 3)
        is_active = True

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        num_nfts = 5
        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, len(token_ids) * payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        self.gofp.stake_tokens_into_session(
            session_id, token_ids, {"from": self.player}
        )

        for token_id in token_ids:
            first_stage_path = self.gofp.get_path_choice(session_id, token_id, 1)
            self.assertEqual(first_stage_path, 0)

        with self.assertRaises(VirtualMachineError):
            self.gofp.choose_current_stage_paths(
                session_id,
                token_ids,
                [token_id % stages[0] + 1 for token_id in token_ids],
                {"from": self.random_person},
            )

        for token_id in token_ids:
            first_stage_path = self.gofp.get_path_choice(session_id, token_id, 1)
            self.assertEqual(first_stage_path, 0)

    def test_player_can_make_a_choice_with_only_surviving_staked_nfts_at_second_stage(
        self,
    ):
        payment_amount = 170
        uri = "https://example.com/test_player_can_make_a_choice_with_only_surviving_staked_nfts_at_second_stage.json"
        stages = (5, 5, 3)
        is_active = True

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        num_nfts = 5
        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, len(token_ids) * payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        self.gofp.stake_tokens_into_session(
            session_id, token_ids, {"from": self.player}
        )

        # First half (rounded down) of tokens will make the correct choice. Rest will make an incorrect
        # choice.
        # Correct path: 3
        first_stage_correct_path = 3
        first_stage_incorrect_path = 2
        num_correct = int(num_nfts / 2)
        first_stage_path_choices = [first_stage_correct_path] * num_correct + [
            first_stage_incorrect_path
        ] * (num_nfts - num_correct)

        self.gofp.choose_current_stage_paths(
            session_id,
            token_ids,
            first_stage_path_choices,
            {"from": self.player},
        )

        expected_correct_tokens = []
        expected_incorrect_tokens = []

        for i, token_id in enumerate(token_ids):
            first_stage_path = self.gofp.get_path_choice(session_id, token_ids[i], 1)
            if i < num_correct:
                self.assertEqual(first_stage_path, first_stage_correct_path)
                expected_correct_tokens.append(token_id)
            else:
                self.assertEqual(first_stage_path, first_stage_incorrect_path)
                expected_incorrect_tokens.append(token_id)

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )
        self.gofp.set_correct_path_for_stage(
            session_id, 1, first_stage_correct_path, True, {"from": self.game_master}
        )

        # Check that current stage has progressed to stage 2
        self.assertEqual(self.gofp.get_current_stage(session_id), 2)

        self.gofp.choose_current_stage_paths(
            session_id,
            expected_correct_tokens,
            [1 for _ in expected_correct_tokens],
            {"from": self.player},
        )

        for token_id in expected_incorrect_tokens:
            with self.assertRaises(VirtualMachineError):
                self.gofp.choose_current_stage_paths(
                    session_id,
                    [token_id],
                    [2],
                    {"from": self.player},
                )

        for token_id in expected_correct_tokens:
            self.assertEqual(self.gofp.get_path_choice(session_id, token_id, 2), 1)

        for token_id in expected_incorrect_tokens:
            self.assertEqual(self.gofp.get_path_choice(session_id, token_id, 2), 0)

    def test_forgiving_session_player_can_make_a_choice_with_any_staked_nfts_at_second_stage(
        self,
    ):
        """
        Checks that, in a forgiving session, even NFTs which made the incorrect choice in the previous
        stage can make a choice in the current stage.

        Also checks that the NFTs which did make incorrect choices in the previous stage are *not* rewarded
        for making a choice in the current stage.
        """
        payment_amount = 1170
        uri = "https://example.com/test_forgiving_session_player_can_make_a_choice_with_any_staked_nfts_at_second_stage.json"
        stages = (5, 5, 3)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            True,  # this session is forgiving
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # Set stage reward for stage 2
        reward_amount = 7
        self.gofp.set_stage_rewards(
            session_id,
            [2],
            [self.terminus.address],
            [self.reward_pool_id],
            [reward_amount],
            {"from": self.game_master},
        )

        self.gofp.set_session_active(session_id, True, {"from": self.game_master})

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        num_nfts = 5
        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, len(token_ids) * payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        self.gofp.stake_tokens_into_session(
            session_id, token_ids, {"from": self.player}
        )

        # First half (rounded down) of tokens will make the correct choice. Rest will make an incorrect
        # choice.
        # Correct path: 3
        first_stage_correct_path = 3
        first_stage_incorrect_path = 2
        num_correct = int(num_nfts / 2)
        first_stage_path_choices = [first_stage_correct_path] * num_correct + [
            first_stage_incorrect_path
        ] * (num_nfts - num_correct)

        self.gofp.choose_current_stage_paths(
            session_id,
            token_ids,
            first_stage_path_choices,
            {"from": self.player},
        )

        expected_correct_tokens = []
        expected_incorrect_tokens = []

        for i, token_id in enumerate(token_ids):
            first_stage_path = self.gofp.get_path_choice(session_id, token_ids[i], 1)
            if i < num_correct:
                self.assertEqual(first_stage_path, first_stage_correct_path)
                expected_correct_tokens.append(token_id)
            else:
                self.assertEqual(first_stage_path, first_stage_incorrect_path)
                expected_incorrect_tokens.append(token_id)

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )
        self.gofp.set_correct_path_for_stage(
            session_id, 1, first_stage_correct_path, True, {"from": self.game_master}
        )

        # Check that current stage has progressed to stage 2
        self.assertEqual(self.gofp.get_current_stage(session_id), 2)

        player_reward_token_balance_0 = self.terminus.balance_of(
            self.player.address, self.reward_pool_id
        )

        self.gofp.choose_current_stage_paths(
            session_id,
            token_ids,
            [1 for _ in token_ids],
            {"from": self.player},
        )

        for token_id in token_ids:
            self.assertEqual(self.gofp.get_path_choice(session_id, token_id, 2), 1)

        player_reward_token_balance_1 = self.terminus.balance_of(
            self.player.address, self.reward_pool_id
        )

        self.assertEqual(
            player_reward_token_balance_1,
            player_reward_token_balance_0
            + len(expected_correct_tokens) * reward_amount,
        )

    def test_player_cannot_make_choice_in_inactive_session(
        self,
    ):
        """
        Tests that a player cannot make a choice in an inactive session.

        Sets up a multi-stage session and allows player to make choices at stage 1.
        After setting the correct path at stage 1, marks the session as inactive and checks that
        player cannot make a choice at stage 2.
        Player has at least one token which made the correct stage 1 choice.
        """
        payment_amount = 174
        uri = "https://example.com/test_player_cannot_make_choice_in_inactive_session.json"
        stages = (5, 5, 3)
        is_active = True

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        num_nfts = 5
        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, len(token_ids) * payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        self.gofp.stake_tokens_into_session(
            session_id, token_ids, {"from": self.player}
        )

        # First half (rounded down) of tokens will make the correct choice. Rest will make an incorrect
        # choice.
        # Correct path: 3
        first_stage_correct_path = 3
        first_stage_incorrect_path = 2
        num_correct = int(num_nfts / 2)
        first_stage_path_choices = [first_stage_correct_path] * num_correct + [
            first_stage_incorrect_path
        ] * (num_nfts - num_correct)

        self.gofp.choose_current_stage_paths(
            session_id,
            token_ids,
            first_stage_path_choices,
            {"from": self.player},
        )

        expected_correct_tokens = []
        expected_incorrect_tokens = []

        for i, token_id in enumerate(token_ids):
            first_stage_path = self.gofp.get_path_choice(session_id, token_ids[i], 1)
            if i < num_correct:
                self.assertEqual(first_stage_path, first_stage_correct_path)
                expected_correct_tokens.append(token_id)
            else:
                self.assertEqual(first_stage_path, first_stage_incorrect_path)
                expected_incorrect_tokens.append(token_id)

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )
        self.gofp.set_correct_path_for_stage(
            session_id, 1, first_stage_correct_path, True, {"from": self.game_master}
        )

        # Check that current stage has progressed to stage 2
        self.assertEqual(self.gofp.get_current_stage(session_id), 2)

        # Mark session as inactive
        self.gofp.set_session_active(session_id, False, {"from": self.game_master})

        with self.assertRaises(VirtualMachineError):
            self.gofp.choose_current_stage_paths(
                session_id,
                expected_correct_tokens,
                [1 for _ in expected_correct_tokens],
                {"from": self.player},
            )

        for token_id in expected_correct_tokens:
            self.assertEqual(self.gofp.get_path_choice(session_id, token_id, 2), 0)

    def test_player_is_rewarded_for_making_a_choice_in_stages_that_have_rewards(
        self,
    ):
        """
        Tests that reward distribution works correctly when a player chooses a path in a stage that
        does have an associated reward.

        Also tests that no rewards are distributed when a player chooses a path in a stage that does
        not have an assocaited reward.

        Test actions:
        1. Create inactive session
        2. Associate a reward with stage 2
        3. Activate session.
        4. Player chooses paths in stage 1
        5. Check that no ERC1155 Transfer events fired in that transaction
        6. Player chooses paths in stage 2
        7. Check that appropriate ERC1155 Transfer event fired in that transaction
        """
        payment_amount = 175
        uri = "https://example.com/test_player_is_rewarded_for_making_a_choice_in_stages_that_have_rewards.json"
        stages = (5, 5, 3)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        reward_amount = 5
        self.gofp.set_stage_rewards(
            session_id,
            [2],
            [self.terminus.address],
            [self.reward_pool_id],
            [reward_amount],
            {"from": self.game_master},
        )

        self.gofp.set_session_active(session_id, True, {"from": self.game_master})

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        num_nfts = 5
        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, len(token_ids) * payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        self.gofp.stake_tokens_into_session(
            session_id, token_ids, {"from": self.player}
        )

        # First half (rounded down) of tokens will make the correct choice. Rest will make an incorrect
        # choice.
        # Correct path: 3
        first_stage_correct_path = 3
        first_stage_incorrect_path = 2
        num_correct = int(num_nfts / 2)
        first_stage_path_choices = [first_stage_correct_path] * num_correct + [
            first_stage_incorrect_path
        ] * (num_nfts - num_correct)

        first_stage_tx_receipt = self.gofp.choose_current_stage_paths(
            session_id,
            token_ids,
            first_stage_path_choices,
            {"from": self.player},
        )

        first_stage_events = _fetch_events_chunk(
            web3_client,
            ERC1155_TRANSFER_SINGLE_EVENT,
            from_block=first_stage_tx_receipt.block_number,
            to_block=first_stage_tx_receipt.block_number,
        )

        self.assertEqual(len(first_stage_events), 0)

        expected_correct_tokens = []

        for i, token_id in enumerate(token_ids):
            if i < num_correct:
                expected_correct_tokens.append(token_id)

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )
        self.gofp.set_correct_path_for_stage(
            session_id, 1, first_stage_correct_path, True, {"from": self.game_master}
        )

        # Check that current stage has progressed to stage 2
        self.assertEqual(self.gofp.get_current_stage(session_id), 2)

        second_stage_tx_receipt = self.gofp.choose_current_stage_paths(
            session_id,
            expected_correct_tokens,
            [1 for _ in expected_correct_tokens],
            {"from": self.player},
        )

        second_stage_events = _fetch_events_chunk(
            web3_client,
            ERC1155_TRANSFER_SINGLE_EVENT,
            from_block=second_stage_tx_receipt.block_number,
            to_block=second_stage_tx_receipt.block_number,
        )

        self.assertEqual(len(second_stage_events), 1)

        erc1155_transfer_single_event = second_stage_events[0]
        self.assertEqual(erc1155_transfer_single_event["args"]["from"], ZERO_ADDRESS)
        self.assertEqual(
            erc1155_transfer_single_event["args"]["to"], self.player.address
        )
        self.assertEqual(
            erc1155_transfer_single_event["args"]["id"], self.reward_pool_id
        )
        self.assertEqual(
            erc1155_transfer_single_event["args"]["value"],
            reward_amount * len(expected_correct_tokens),
        )

    def test_player_is_rewarded_for_choosing_path_that_has_reward(
        self,
    ):
        """
        Tests that reward distribution works correctly when a player chooses a path that
        has an associated path reward.

        Also tests that no rewards are distributed when a player chooses a path that
        does not have an associated reward.

        Test actions:
        1. Create inactive, forgiving session
        2. Associate rewards with stage 1 path 2, stage 2 paths 1 and 2, stage 3 path 1.
        3. Activate session.
        4. Player chooses paths in stage 1
        5. Check that appropriate ERC1155 Transfer events are fired in that transaction
        6. Player chooses paths in stage 2
        7. Check that appropriate ERC1155 Transfer events are fired in that transaction
        8. Player chooses paths in stage 3
        9. Check that appropriate ERC1155 Transfer events are fired in that transaction
        """
        payment_amount = 175
        uri = "https://example.com/test_player_is_rewarded_for_choosing_path_that_has_reward.json"
        stages = (2, 3, 1)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            True,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # Rewards for all paths except for stage 1 path 1 and stage 2 path 3.
        stages_with_rewards = [1, 2, 2, 3]
        paths_with_rewards = [2, 1, 2, 1]

        self.gofp.set_path_rewards(
            session_id,
            stages_with_rewards,
            paths_with_rewards,
            [self.terminus.address] * len(stages_with_rewards),
            [self.reward_pool_id] * len(stages_with_rewards),
            [
                (2**stage) * (3**path)
                for stage, path in zip(stages_with_rewards, paths_with_rewards)
            ],
            {"from": self.game_master},
        )

        self.gofp.set_session_active(session_id, True, {"from": self.game_master})

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        num_nfts = 8
        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, len(token_ids) * payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        self.gofp.stake_tokens_into_session(
            session_id, token_ids, {"from": self.player}
        )

        # First half (rounded up) of tokens will choose path 1. Rest will choose path 2.
        first_stage_path_1_count = math.ceil(num_nfts / 2)
        first_stage_path_2_count = math.floor(num_nfts / 2)
        first_stage_path_choices = [1] * first_stage_path_1_count + [
            2
        ] * first_stage_path_2_count

        first_stage_tx_receipt = self.gofp.choose_current_stage_paths(
            session_id,
            token_ids,
            first_stage_path_choices,
            {"from": self.player},
        )

        first_stage_events = _fetch_events_chunk(
            web3_client,
            ERC1155_TRANSFER_SINGLE_EVENT,
            from_block=first_stage_tx_receipt.block_number,
            to_block=first_stage_tx_receipt.block_number,
        )

        self.assertEqual(len(first_stage_events), first_stage_path_2_count)

        for i, erc1155_transfer_event in enumerate(first_stage_events):
            self.assertEqual(erc1155_transfer_event["args"]["from"], ZERO_ADDRESS)
            self.assertEqual(erc1155_transfer_event["args"]["to"], self.player.address)
            self.assertEqual(erc1155_transfer_event["args"]["id"], self.reward_pool_id)
            self.assertEqual(
                erc1155_transfer_event["args"]["value"],
                (2**1) * (3**2),
            )

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )
        self.gofp.set_correct_path_for_stage(
            session_id, 1, 1, True, {"from": self.game_master}
        )

        # Check that current stage has progressed to stage 2
        self.assertEqual(self.gofp.get_current_stage(session_id), 2)

        second_stage_path_choices = list(
            map(lambda x: (x % 3) if (x % 3) > 0 else 3, range(1, num_nfts + 1))
        )

        second_stage_tx_receipt = self.gofp.choose_current_stage_paths(
            session_id,
            token_ids,
            second_stage_path_choices,
            {"from": self.player},
        )

        second_stage_events = _fetch_events_chunk(
            web3_client,
            ERC1155_TRANSFER_SINGLE_EVENT,
            from_block=second_stage_tx_receipt.block_number,
            to_block=second_stage_tx_receipt.block_number,
        )

        # First two of three paths in second stage have rewards
        self.assertEqual(len(second_stage_events), math.ceil(2 / 3 * num_nfts))

        for i, erc1155_transfer_event in enumerate(second_stage_events):
            self.assertEqual(erc1155_transfer_event["args"]["from"], ZERO_ADDRESS)
            self.assertEqual(erc1155_transfer_event["args"]["to"], self.player.address)
            self.assertEqual(erc1155_transfer_event["args"]["id"], self.reward_pool_id)
            self.assertEqual(
                erc1155_transfer_event["args"]["value"],
                (2**2) * (3 ** (i % 2 + 1)),
            )

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )
        # Correct path doesn't affect path rewards.
        self.gofp.set_correct_path_for_stage(
            session_id, 2, 1, True, {"from": self.game_master}
        )

        # Check that current stage has progressed to stage 3
        self.assertEqual(self.gofp.get_current_stage(session_id), 3)

        third_stage_tx_receipt = self.gofp.choose_current_stage_paths(
            session_id,
            token_ids,
            [1] * num_nfts,
            {"from": self.player},
        )

        third_stage_events = _fetch_events_chunk(
            web3_client,
            ERC1155_TRANSFER_SINGLE_EVENT,
            from_block=third_stage_tx_receipt.block_number,
            to_block=third_stage_tx_receipt.block_number,
        )

        # Only 1 path so all nfts get reward
        self.assertEqual(len(third_stage_events), num_nfts)

        for i, erc1155_transfer_event in enumerate(third_stage_events):
            self.assertEqual(erc1155_transfer_event["args"]["from"], ZERO_ADDRESS)
            self.assertEqual(erc1155_transfer_event["args"]["to"], self.player.address)
            self.assertEqual(erc1155_transfer_event["args"]["id"], self.reward_pool_id)
            self.assertEqual(
                erc1155_transfer_event["args"]["value"],
                (2**3) * (3**1),
            )

    def test_player_can_receive_different_pool_ids_in_stage_and_path_rewards(
        self,
    ):
        """
        Tests that reward distribution works correctly when a player receives rewards with different pool ids.

        Test actions:
        1. Create inactive, forgiving session
        2. Associate different rewards with stages 1 and 2
        3. Associate different rewards with stage 1 path 1 and stage 2 path 1
        4. Activate session.
        5. Player chooses path in stage 1
        6. Check that appropriate ERC1155 Transfer events are fired in that transaction
        7. Player chooses path in stage 2
        8. Check that appropriate ERC1155 Transfer events are fired in that transaction
        """
        payment_amount = 175
        uri = "https://example.com/test_player_can_receive_different_pool_ids_in_stage_and_path_rewards.json"
        stages = (1, 1)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            True,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # Rewards for all paths except for stage 1 path 1 and stage 2 path 3.
        stages_with_rewards = [1, 2]
        stage_rewards_pool_ids = [self.reward_pool_id, self.reward_2_pool_id]
        stage_reward_amounts = [1, 2]

        paths_with_rewards = [1, 1]
        path_reward_pool_ids = [self.reward_3_pool_id, self.reward_4_pool_id]
        path_reward_amounts = [3, 4]

        self.gofp.set_stage_rewards(
            session_id,
            stages_with_rewards,
            [self.terminus.address] * len(stages_with_rewards),
            stage_rewards_pool_ids,
            stage_reward_amounts,
            {"from": self.game_master},
        )

        self.gofp.set_path_rewards(
            session_id,
            stages_with_rewards,
            paths_with_rewards,
            [self.terminus.address] * len(stages_with_rewards),
            path_reward_pool_ids,
            path_reward_amounts,
            {"from": self.game_master},
        )

        self.gofp.set_session_active(session_id, True, {"from": self.game_master})

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()
        token_id = total_nfts + 1

        self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        self.gofp.stake_tokens_into_session(
            session_id, [token_id], {"from": self.player}
        )

        first_stage_tx_receipt = self.gofp.choose_current_stage_paths(
            session_id,
            [token_id],
            [1],
            {"from": self.player},
        )

        first_stage_events = _fetch_events_chunk(
            web3_client,
            ERC1155_TRANSFER_SINGLE_EVENT,
            from_block=first_stage_tx_receipt.block_number,
            to_block=first_stage_tx_receipt.block_number,
        )

        self.assertEqual(len(first_stage_events), 2)

        for i, erc1155_transfer_event in enumerate(first_stage_events):
            self.assertEqual(erc1155_transfer_event["args"]["from"], ZERO_ADDRESS)
            self.assertEqual(erc1155_transfer_event["args"]["to"], self.player.address)
            pool_id = erc1155_transfer_event["args"]["id"]
            value = erc1155_transfer_event["args"]["value"]
            if pool_id == self.reward_pool_id:
                self.assertEqual(value, 1)
            elif pool_id == self.reward_3_pool_id:
                self.assertEqual(value, 3)
            else:
                self.fail("Received incorrect pool id in reward event.")

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )
        self.gofp.set_correct_path_for_stage(
            session_id, 1, 1, True, {"from": self.game_master}
        )

        # Check that current stage has progressed to stage 2
        self.assertEqual(self.gofp.get_current_stage(session_id), 2)

        second_stage_tx_receipt = self.gofp.choose_current_stage_paths(
            session_id,
            [token_id],
            [1],
            {"from": self.player},
        )

        second_stage_events = _fetch_events_chunk(
            web3_client,
            ERC1155_TRANSFER_SINGLE_EVENT,
            from_block=second_stage_tx_receipt.block_number,
            to_block=second_stage_tx_receipt.block_number,
        )

        # First two of three paths in second stage have rewards
        self.assertEqual(len(second_stage_events), 2)

        for i, erc1155_transfer_event in enumerate(second_stage_events):
            self.assertEqual(erc1155_transfer_event["args"]["from"], ZERO_ADDRESS)
            self.assertEqual(erc1155_transfer_event["args"]["to"], self.player.address)
            pool_id = erc1155_transfer_event["args"]["id"]
            value = erc1155_transfer_event["args"]["value"]
            if pool_id == self.reward_2_pool_id:
                self.assertEqual(value, 2)
            elif pool_id == self.reward_4_pool_id:
                self.assertEqual(value, 4)
            else:
                self.fail("Received incorrect pool id in reward event.")

    def test_player_cannnot_make_a_choice_with_same_token_twice(self):
        payment_amount = 176
        uri = "https://example.com/test_player_cannnot_make_a_choice_with_same_token_twice.json"
        stages = (5, 5, 3)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        reward_amount = 6
        self.gofp.set_stage_rewards(
            session_id,
            [1],
            [self.terminus.address],
            [self.reward_pool_id],
            [reward_amount],
            {"from": self.game_master},
        )

        self.gofp.set_session_active(session_id, True, {"from": self.game_master})

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        num_nfts = 5
        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, len(token_ids) * payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        self.gofp.stake_tokens_into_session(
            session_id, token_ids, {"from": self.player}
        )

        for token_id in token_ids:
            first_stage_path = self.gofp.get_path_choice(session_id, token_id, 1)
            self.assertEqual(first_stage_path, 0)

        reward_balance_0 = self.terminus.balance_of(
            self.player.address, self.reward_pool_id
        )

        self.gofp.choose_current_stage_paths(
            session_id,
            token_ids,
            [token_id % stages[0] + 1 for token_id in token_ids],
            {"from": self.player},
        )

        reward_balance_1 = self.terminus.balance_of(
            self.player.address, self.reward_pool_id
        )
        self.assertEqual(
            reward_balance_1, reward_balance_0 + len(token_ids) * reward_amount
        )

        for token_id in token_ids:
            first_stage_path = self.gofp.get_path_choice(session_id, token_id, 1)
            self.assertEqual(first_stage_path, token_id % stages[0] + 1)

        with self.assertRaises(VirtualMachineError):
            self.gofp.choose_current_stage_paths(
                session_id,
                token_ids,
                [token_id % stages[0] + 1 for token_id in token_ids],
                {"from": self.player},
            )

        reward_balance_2 = self.terminus.balance_of(
            self.player.address, self.reward_pool_id
        )
        self.assertEqual(reward_balance_2, reward_balance_1)

    def test_player_can_unstake_from_active_session_not_restake_into_same_session_but_stake_into_new_session(
        self,
    ):
        """
        This tests that players can unstake from an active session but not restake into the same session.
        It also tests that players are able to stake tokens that were unstaked from a session into *other*
        active sessions that they were not previously staked in.
        It tests for regression of a bug that existed in a development version of this contract.
        """
        payment_amount = 177
        uri = "https://example.com/test_player_can_unstake_from_active_session_not_restake_into_same_session_but_stake_into_new_session.json"
        stages = (5, 5, 3)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        reward_amount = 6
        self.gofp.set_stage_rewards(
            session_id,
            [1],
            [self.terminus.address],
            [self.reward_pool_id],
            [reward_amount],
            {"from": self.game_master},
        )

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        num_nfts = 5
        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, len(token_ids) * payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        self.gofp.set_session_active(session_id, True, {"from": self.game_master})

        num_staked_0 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_0 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_0 = self.nft.balance_of(self.gofp.address)

        self.gofp.stake_tokens_into_session(
            session_id, token_ids, {"from": self.player}
        )

        num_staked_1 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_1 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_1 = self.nft.balance_of(self.gofp.address)

        self.assertEqual(num_staked_1, num_staked_0 + len(token_ids))
        self.assertEqual(num_owned_by_player_1, num_owned_by_player_0 - len(token_ids))
        self.assertEqual(
            num_owned_by_contract_1, num_owned_by_contract_0 + len(token_ids)
        )

        for token_id in token_ids:
            staked_session_id, owner = self.gofp.get_staked_token_info(
                self.nft.address, token_id
            )
            self.assertEqual(staked_session_id, session_id)
            self.assertEqual(owner, self.player.address)

        for i, token_id in enumerate(token_ids):
            self.assertEqual(
                self.gofp.token_of_staker_in_session_by_index(
                    session_id,
                    self.player.address,
                    num_staked_1 - len(token_ids) + 1 + i,
                ),
                token_ids[i],
            )
            self.assertEqual(self.nft.owner_of(token_id), self.gofp.address)

        # Now we check that unstaking and restaking doesn't override path choices at previous stage
        # 1 is the correct choice
        path_choices = [1] + [2 for _ in token_ids[1:]]
        self.gofp.choose_current_stage_paths(
            session_id, token_ids, path_choices, {"from": self.player}
        )

        self.gofp.unstake_tokens_from_session(
            session_id, token_ids, {"from": self.player}
        )

        num_staked_2 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_2 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_2 = self.nft.balance_of(self.gofp.address)

        self.assertEqual(num_staked_2, num_staked_0)
        self.assertEqual(num_owned_by_player_2, num_owned_by_player_0)
        self.assertEqual(num_owned_by_contract_2, num_owned_by_contract_0)
        self.assertEqual(
            self.gofp.token_of_staker_in_session_by_index(
                session_id, self.player.address, 1
            ),
            0,
        )

        for i, token_id in enumerate(token_ids):
            staked_session_id, owner = self.gofp.get_staked_token_info(
                self.nft.address, token_id
            )
            self.assertEqual(staked_session_id, 0)
            self.assertEqual(owner, ZERO_ADDRESS)

            self.assertEqual(
                self.gofp.token_of_staker_in_session_by_index(
                    session_id,
                    self.player.address,
                    num_staked_2 + 1 + i,
                ),
                0,
            )
            self.assertEqual(self.nft.owner_of(token_id), self.player.address)

        with self.assertRaises(VirtualMachineError):
            self.gofp.stake_tokens_into_session(
                session_id, token_ids, {"from": self.player}
            )

        num_staked_3 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_3 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_3 = self.nft.balance_of(self.gofp.address)

        self.assertEqual(num_staked_3, num_staked_2)
        self.assertEqual(num_owned_by_player_3, num_owned_by_player_2)
        self.assertEqual(num_owned_by_contract_3, num_owned_by_contract_2)

        self.assertEqual(self.gofp.get_path_choice(session_id, token_ids[0], 1), 1)
        for token_id in token_ids[1:]:
            self.assertEqual(self.gofp.get_path_choice(session_id, token_id, 1), 2)

        self.gofp.create_session(
            self.nft.address,
            ZERO_ADDRESS,
            0,
            True,
            "https://example.com/new_session.json",
            stages,
            True,
            {"from": self.game_master},
        )

        new_session_id = self.gofp.num_sessions()

        num_staked_new_0 = self.gofp.num_tokens_staked_into_session(
            new_session_id, self.player.address
        )
        num_owned_by_player_new_0 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_new_0 = self.nft.balance_of(self.gofp.address)

        self.gofp.stake_tokens_into_session(
            new_session_id, token_ids, {"from": self.player}
        )

        num_staked_new_1 = self.gofp.num_tokens_staked_into_session(
            new_session_id, self.player.address
        )
        num_owned_by_player_new_1 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_new_1 = self.nft.balance_of(self.gofp.address)

        self.assertEqual(num_staked_new_1, num_staked_new_0 + len(token_ids))
        self.assertEqual(
            num_owned_by_player_new_1, num_owned_by_player_new_0 - len(token_ids)
        )
        self.assertEqual(
            num_owned_by_contract_new_1, num_owned_by_contract_new_0 + len(token_ids)
        )

        for i, token_id in enumerate(token_ids):
            staked_new_session_id, owner = self.gofp.get_staked_token_info(
                self.nft.address, token_id
            )
            self.assertEqual(staked_new_session_id, new_session_id)
            self.assertEqual(owner, self.player.address)

            self.assertEqual(
                self.gofp.token_of_staker_in_session_by_index(
                    new_session_id,
                    self.player.address,
                    num_staked_new_1 - len(token_ids) + 1 + i,
                ),
                token_ids[i],
            )
            self.assertEqual(self.nft.owner_of(token_id), self.gofp.address)


class TestFullGames(GOFPTestCase):
    # TODO(zomglings): Test the following functionality:
    # - Test multiplayer game
    def test_single_player_game(self):
        payment_amount = 337
        uri = "https://example.com/test_single_player_game.json"
        # NOTE: The test assumes that there are 3 stages. You can change the number of paths per change,
        # but do not change the number of stages.
        # The stage numbers also need to be coprime to each other - Chinese Remainder Theorem!
        stages = (2, 3, 5)
        correct_paths = (2, 1, 3)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # We set rewards for each stage
        reward_amounts = [1, 2, 4]
        self.gofp.set_stage_rewards(
            session_id,
            [1, 2, 3],
            [self.terminus.address] * 3,
            [self.reward_pool_id] * 3,
            reward_amounts,
            {"from": self.game_master},
        )

        # First path has reward on each stage
        self.gofp.set_path_rewards(
            session_id,
            [1, 2, 3],
            [1, 1, 1],
            [self.terminus.address] * 3,
            [self.reward_pool_id] * 3,
            [1, 1, 1],
            {"from": self.game_master},
        )

        self.gofp.set_session_active(session_id, True, {"from": self.game_master})

        # We create a second session to ensure that the NFTs are being staked into the right session.
        # There was a bug in a development version of the contract in which the staking function was
        # checking if the most *recent* session was active instead of the session with the given sessionId.
        # This means that, if the most recent function were inactive, players wouldn't be able to stake
        # eligible tokens even into an active session.
        self.gofp.create_session(
            self.random_person.address,
            ZERO_ADDRESS,
            0,
            False,
            "https://example.com/wrong_session.json",
            (1,),
            False,
            {"from": self.game_master},
        )

        # Player will distribute NFTs evenly across choices at every stage. So we give them enough NFTs
        # to have a single winning NFT at the end of the game.
        # So if stages = (2, 3, 5), num_nfts = 2 * 3 * 5 = 30.
        num_nfts = 1
        for i in stages:
            num_nfts *= i

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, len(token_ids) * payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        self.gofp.stake_tokens_into_session(
            session_id, token_ids, {"from": self.player}
        )

        # **Stage 1**
        first_stage_path_choices = [token_id % stages[0] + 1 for token_id in token_ids]
        first_stage_correct_token_ids = [
            token_id
            for token_id in token_ids
            if token_id % stages[0] + 1 == correct_paths[0]
        ]
        # Sanity check for test setup
        self.assertEqual(len(first_stage_correct_token_ids), int(num_nfts / stages[0]))

        player_reward_token_balance_0 = self.terminus.balance_of(
            self.player.address, self.reward_pool_id
        )

        self.gofp.choose_current_stage_paths(
            session_id,
            token_ids,
            first_stage_path_choices,
            {"from": self.player},
        )

        player_reward_token_balance_1 = self.terminus.balance_of(
            self.player.address, self.reward_pool_id
        )
        self.assertEqual(
            player_reward_token_balance_1,
            player_reward_token_balance_0
            # stage rewards
            + int(reward_amounts[0] * len(token_ids))
            # path rewards
            + int(1 * len(token_ids) / stages[0]),
        )

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )
        self.gofp.set_correct_path_for_stage(
            session_id, 1, correct_paths[0], True, {"from": self.game_master}
        )

        # Check that current stage has progressed to stage 2
        self.assertEqual(self.gofp.get_current_stage(session_id), 2)

        for token_id in token_ids:
            if token_id not in first_stage_correct_token_ids:
                with self.assertRaises(VirtualMachineError):
                    self.gofp.choose_current_stage_paths(
                        session_id,
                        [token_id],
                        [1],
                        {"from": self.player},
                    )

        # **Stage 2**
        second_stage_path_choices = [
            token_id % stages[1] + 1 for token_id in first_stage_correct_token_ids
        ]
        second_stage_correct_token_ids = [
            token_id
            for token_id in first_stage_correct_token_ids
            if token_id % stages[1] + 1 == correct_paths[1]
        ]

        # Sanity check for test setup
        self.assertEqual(
            len(second_stage_correct_token_ids), int(num_nfts / (stages[0] * stages[1]))
        )

        self.gofp.choose_current_stage_paths(
            session_id,
            first_stage_correct_token_ids,
            second_stage_path_choices,
            {"from": self.player},
        )

        player_reward_token_balance_2 = self.terminus.balance_of(
            self.player.address, self.reward_pool_id
        )
        self.assertEqual(
            player_reward_token_balance_2,
            player_reward_token_balance_1
            # stage rewards
            + int(reward_amounts[1] * len(token_ids) / stages[0])
            # path rewards
            + int(1 * len(first_stage_correct_token_ids) / stages[1]),
        )

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )
        self.gofp.set_correct_path_for_stage(
            session_id, 2, correct_paths[1], True, {"from": self.game_master}
        )

        # Check that current stage has progressed to stage 3
        self.assertEqual(self.gofp.get_current_stage(session_id), 3)

        for token_id in token_ids:
            if token_id not in second_stage_correct_token_ids:
                with self.assertRaises(VirtualMachineError):
                    self.gofp.choose_current_stage_paths(
                        session_id,
                        [token_id],
                        [1],
                        {"from": self.player},
                    )

        # **Stage 3**
        third_stage_path_choices = [
            token_id % stages[2] + 1 for token_id in second_stage_correct_token_ids
        ]

        third_stage_correct_token_ids = [
            token_id
            for token_id in second_stage_correct_token_ids
            if token_id % stages[2] + 1 == correct_paths[2]
        ]
        # Sanity check for test setup
        self.assertEqual(len(third_stage_correct_token_ids), 1)

        self.gofp.choose_current_stage_paths(
            session_id,
            second_stage_correct_token_ids,
            third_stage_path_choices,
            {"from": self.player},
        )

        player_reward_token_balance_3 = self.terminus.balance_of(
            self.player.address, self.reward_pool_id
        )
        self.assertEqual(
            player_reward_token_balance_3,
            player_reward_token_balance_2
            # stage rewards
            + int(reward_amounts[2] * len(token_ids) / (stages[0] * stages[1]))
            # path rewards
            + int(1 * len(second_stage_correct_token_ids) / stages[2]),
        )

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )
        self.gofp.set_correct_path_for_stage(
            session_id, 3, correct_paths[2], True, {"from": self.game_master}
        )

        # Check that current stage has progressed to stage 4
        self.assertEqual(self.gofp.get_current_stage(session_id), 4)

        for token_id in token_ids:
            with self.assertRaises(VirtualMachineError):
                self.gofp.choose_current_stage_paths(
                    session_id,
                    [token_id],
                    [1],
                    {"from": self.player},
                )

    def test_forgiving_single_player_game(self):
        """
        This test works very similarly to test_single_player_game. The tokens that made the incorrect
        choice on the previous stage all make the correct choice on the subsequent stage.
        """
        payment_amount = 338
        uri = "https://example.com/test_forgiving_single_player_game.json"
        # NOTE: The test assumes that there are 3 stages. You can change the number of paths per change,
        # but do not change the number of stages.
        # The stage numbers also need to be coprime to each other - Chinese Remainder Theorem!
        stages = (2, 3, 5)
        correct_paths = (2, 1, 3)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            True,  # this session is forgiving
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # We set rewards for each stage
        reward_amounts = [1, 2, 4]
        self.gofp.set_stage_rewards(
            session_id,
            [1, 2, 3],
            [self.terminus.address] * 3,
            [self.reward_pool_id] * 3,
            reward_amounts,
            {"from": self.game_master},
        )

        # First path has reward on each stage
        self.gofp.set_path_rewards(
            session_id,
            [1, 2, 3],
            [1, 1, 1],
            [self.terminus.address] * 3,
            [self.reward_pool_id] * 3,
            [1, 1, 1],
            {"from": self.game_master},
        )

        self.gofp.set_session_active(session_id, True, {"from": self.game_master})

        # We create a second session to ensure that the NFTs are being staked into the right session.
        # There was a bug in a development version of the contract in which the staking function was
        # checking if the most *recent* session was active instead of the session with the given sessionId.
        # This means that, if the most recent function were inactive, players wouldn't be able to stake
        # eligible tokens even into an active session.
        self.gofp.create_session(
            self.random_person.address,
            ZERO_ADDRESS,
            0,
            False,
            "https://example.com/wrong_session.json",
            (1,),
            False,
            {"from": self.game_master},
        )

        # Player will distribute NFTs evenly across choices at every stage. So we give them enough NFTs
        # to have a single winning NFT at the end of the game.
        # So if stages = (2, 3, 5), num_nfts = 2 * 3 * 5 = 30.
        num_nfts = 1
        for i in stages:
            num_nfts *= i

        # Mint NFTs to the player
        total_nfts = self.nft.total_supply()

        token_ids = [total_nfts + i for i in range(1, num_nfts + 1)]

        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})

        # Mint num_tokens*payment_amount of payment_token to player
        self.payment_token.mint(
            self.player.address, len(token_ids) * payment_amount, {"from": self.owner}
        )

        self.payment_token.approve(self.gofp.address, MAX_UINT, {"from": self.player})
        self.nft.set_approval_for_all(self.gofp.address, True, {"from": self.player})

        self.gofp.stake_tokens_into_session(
            session_id, token_ids, {"from": self.player}
        )

        # **Stage 1**
        first_stage_path_choices = [token_id % stages[0] + 1 for token_id in token_ids]
        first_stage_correct_token_ids = [
            token_id
            for token_id in token_ids
            if token_id % stages[0] + 1 == correct_paths[0]
        ]
        # Sanity check for test setup
        self.assertEqual(len(first_stage_correct_token_ids), int(num_nfts / stages[0]))

        player_reward_token_balance_0 = self.terminus.balance_of(
            self.player.address, self.reward_pool_id
        )

        self.gofp.choose_current_stage_paths(
            session_id,
            token_ids,
            first_stage_path_choices,
            {"from": self.player},
        )

        player_reward_token_balance_1 = self.terminus.balance_of(
            self.player.address, self.reward_pool_id
        )
        self.assertEqual(
            player_reward_token_balance_1,
            player_reward_token_balance_0
            # stage rewards
            + int(reward_amounts[0] * len(token_ids))
            # path rewards
            + int(1 * len(token_ids) / stages[0]),
        )

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )
        self.gofp.set_correct_path_for_stage(
            session_id, 1, correct_paths[0], True, {"from": self.game_master}
        )

        # Check that current stage has progressed to stage 2
        self.assertEqual(self.gofp.get_current_stage(session_id), 2)

        # **Stage 2**
        second_stage_path_choices = [token_id % stages[1] + 1 for token_id in token_ids]
        second_stage_correct_token_ids = [
            token_id
            for token_id in token_ids
            if token_id % stages[1] + 1 == correct_paths[1]
        ]

        # Sanity check for test setup
        self.assertEqual(len(second_stage_correct_token_ids), int(num_nfts / stages[1]))

        self.gofp.choose_current_stage_paths(
            session_id,
            token_ids,
            second_stage_path_choices,
            {"from": self.player},
        )

        player_reward_token_balance_2 = self.terminus.balance_of(
            self.player.address, self.reward_pool_id
        )
        self.assertEqual(
            player_reward_token_balance_2,
            player_reward_token_balance_1
            # stage rewards
            + reward_amounts[1] * int(len(token_ids) / stages[0])
            # path rewards
            + int(1 * len(token_ids) / stages[1]),
        )

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )
        self.gofp.set_correct_path_for_stage(
            session_id, 2, correct_paths[1], True, {"from": self.game_master}
        )

        # Check that current stage has progressed to stage 3
        self.assertEqual(self.gofp.get_current_stage(session_id), 3)

        second_stage_incorrect_token_ids = [
            token_id
            for token_id in token_ids
            if token_id not in second_stage_correct_token_ids
        ]

        # **Stage 3**
        third_stage_path_choices = [token_id % stages[2] + 1 for token_id in token_ids]

        third_stage_correct_token_ids = [
            token_id
            for token_id in token_ids
            if token_id % stages[2] + 1 == correct_paths[2]
        ]

        # Sanity check for test setup
        self.assertEqual(len(third_stage_correct_token_ids), int(num_nfts / stages[2]))

        self.gofp.choose_current_stage_paths(
            session_id,
            token_ids,
            third_stage_path_choices,
            {"from": self.player},
        )

        player_reward_token_balance_3 = self.terminus.balance_of(
            self.player.address, self.reward_pool_id
        )
        self.assertEqual(
            player_reward_token_balance_3,
            player_reward_token_balance_2
            # stage rewards
            + reward_amounts[2] * int(len(token_ids) / stages[1])
            # path rewards
            + int(1 * len(token_ids) / stages[2]),
        )

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )
        self.gofp.set_correct_path_for_stage(
            session_id, 3, correct_paths[2], True, {"from": self.game_master}
        )

        # Check that current stage has progressed to stage 4
        self.assertEqual(self.gofp.get_current_stage(session_id), 4)

        for token_id in token_ids:
            with self.assertRaises(VirtualMachineError):
                self.gofp.choose_current_stage_paths(
                    session_id,
                    [token_id],
                    [1],
                    {"from": self.player},
                )


class TestCallbacks(GOFPTestCase):
    def test_session_staking_predicate(self):
        """
        Tests administrators' ability to register and view staking predicate for a given session.
        The staking predicate is called once per token that a user tries to stake into the session.
        It is called with three arguments appended to its calldata:
        1. The address of player who is trying to stake the token.
        2. The address of the ERC721 contract that the token belongs to.
        3. The token ID.

        The predicate is expected to return true/false.

        Test actions:
        1. Create inactive session
        2. Check that no predicate is registered for that session.
        3. Register a predicate for that session.
        4. Check that predicate was registered correctly.
        5. Call that predicate through the GOFP contract to make sure call logic functions as intended.
        """
        payment_amount = 0
        uri = "https://example.com/test_session_staking_predicate.json"
        stages = (4, 1)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        """
        Predicate structure:
        struct Predicate {
            address predicateAddress;
            bytes4 functionSelector;
            // initialArguments is intended to be the ABIen
            bytes initialArguments;
            uint256 initialArgumentsLength;
        }
        """
        initial_predicate = self.gofp.get_session_staking_predicate(session_id)
        self.assertEqual(initial_predicate, (ZERO_ADDRESS, "0x0", "0x0"))

        encoded_predicate_with_dummy_end_values = (
            self.gofp_predicates.contract.doesNotExceedMaxTokensInSession.encode_input(
                1, self.gofp.address, session_id, ZERO_ADDRESS, ZERO_ADDRESS, 0
            )
        )
        encoded_predicate_initial_args = encoded_predicate_with_dummy_end_values[
            10 : len(encoded_predicate_with_dummy_end_values) - 96 * 2
        ]

        # GOFPPredicates.doesNotExceedMaxTokensInSession selector - calculated using -annotations flag on solface: https://github.com/bugout-dev/solface.
        predicate_selector = "0x52760e08"

        with self.assertRaises(VirtualMachineError):
            self.gofp.set_session_staking_predicate(
                session_id,
                predicate_selector,
                self.gofp_predicates.address,
                encoded_predicate_initial_args,
                {"from": self.player},
            )

        self.gofp.set_session_staking_predicate(
            session_id,
            predicate_selector,
            self.gofp_predicates.address,
            encoded_predicate_initial_args,
            {"from": self.game_master},
        )

        predicate = self.gofp.get_session_staking_predicate(session_id)
        self.assertEqual(
            predicate,
            (
                self.gofp_predicates.address,
                predicate_selector,
                f"0x{encoded_predicate_initial_args}",
            ),
        )

        num_nfts = self.nft.total_supply()
        token_ids = [num_nfts + 1, num_nfts + 2]
        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})
            self.nft.approve(self.gofp.address, token_id, {"from": self.player})

        check_0 = self.gofp.call_session_staking_predicate(
            session_id, self.player.address, token_ids[0]
        )
        self.assertTrue(check_0)

        self.gofp.set_session_active(session_id, True, {"from": self.game_master})

        self.gofp.stake_tokens_into_session(
            session_id, [token_ids[0]], {"from": self.player}
        )

        check_1 = self.gofp.call_session_staking_predicate(
            session_id, self.player.address, token_ids[1]
        )
        self.assertFalse(check_1)

        with self.assertRaises(VirtualMachineError):
            self.gofp.stake_tokens_into_session(
                session_id, [token_ids[1]], {"from": self.player}
            )

    def test_path_choice_predicate(self):
        """
        Tests administrators' ability to register and view path choice predicate for a specified path.
        The path choice predicate is called when user tries to choice the specified path.
        It is called with three arguments appended to its calldata:
        1. The address of player who is trying to stake the token.
        2. The address of the ERC721 contract that the token belongs to.
        3. The token ID.

        The predicate is expected to return true/false.

        Test actions:
        1. Create inactive session
        2. Check that no predicate is registered for the specified path.
        3. Register a predicate for specified path.
        4. Check that predicate was registered correctly.
        5. Call that predicate through the GOFP contract to make sure call logic functions as intended.
        6. Verify path can be selected when predicate passes.
        7. Verify path cannot be selected when predicate fails.
        8. Verify that a different path can be selected when predicate fails.
        """
        payment_amount = 0
        uri = "https://example.com/test_path_choice_predicate.json"
        stages = (4, 1)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            False,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()
        stage_with_path_choice_predicate = 1
        path_without_predicate = 1
        path_with_path_choice_predicate = 2
        """
        Predicate structure:
        struct Predicate {
            address predicateAddress;
            bytes4 functionSelector;
            // initialArguments is intended to be the ABIen
            bytes initialArguments;
            uint256 initialArgumentsLength;
        }
        """
        initial_predicate = self.gofp.get_path_choice_predicate(
            (
                session_id,
                stage_with_path_choice_predicate,
                path_with_path_choice_predicate,
            )
        )
        self.assertEqual(initial_predicate, (ZERO_ADDRESS, "0x0", "0x0"))

        encoded_predicate_with_dummy_end_values = (
            self.gofp_predicates.contract.doesNotExceedMaxTokensInSession.encode_input(
                2, self.gofp.address, session_id, ZERO_ADDRESS, ZERO_ADDRESS, 0
            )
        )
        encoded_predicate_initial_args = encoded_predicate_with_dummy_end_values[
            10 : len(encoded_predicate_with_dummy_end_values) - 96 * 2
        ]

        # GOFPPredicates.doesNotExceedMaxTokensInSession selector - calculated using -annotations flag on solface: https://github.com/bugout-dev/solface.
        predicate_selector = "0x52760e08"

        with self.assertRaises(VirtualMachineError):
            self.gofp.set_path_choice_predicate(
                (
                    session_id,
                    stage_with_path_choice_predicate,
                    path_with_path_choice_predicate,
                ),
                predicate_selector,
                self.gofp_predicates.address,
                encoded_predicate_initial_args,
                {"from": self.player},
            )

        self.gofp.set_path_choice_predicate(
            (
                session_id,
                stage_with_path_choice_predicate,
                path_with_path_choice_predicate,
            ),
            predicate_selector,
            self.gofp_predicates.address,
            encoded_predicate_initial_args,
            {"from": self.game_master},
        )

        predicate = self.gofp.get_path_choice_predicate(
            (
                session_id,
                stage_with_path_choice_predicate,
                path_with_path_choice_predicate,
            )
        )
        self.assertEqual(
            predicate,
            (
                self.gofp_predicates.address,
                predicate_selector,
                f"0x{encoded_predicate_initial_args}",
            ),
        )

        num_nfts = self.nft.total_supply()
        token_ids = [num_nfts + 1, num_nfts + 2]
        for token_id in token_ids:
            self.nft.mint(self.player.address, token_id, {"from": self.owner})
            self.nft.approve(self.gofp.address, token_id, {"from": self.player})

        self.gofp.set_session_active(session_id, True, {"from": self.game_master})
        self.gofp.set_session_choosing_active(
            session_id, True, {"from": self.game_master}
        )

        # First token
        self.gofp.stake_tokens_into_session(
            session_id, [token_ids[0]], {"from": self.player}
        )
        check_0 = self.gofp.call_path_choice_predicate(
            (
                session_id,
                stage_with_path_choice_predicate,
                path_with_path_choice_predicate,
            ),
            self.player.address,
            token_ids[0],
        )
        self.assertTrue(check_0)

        # With one token staked predicate should still pass
        self.gofp.choose_current_stage_paths(
            session_id,
            [token_ids[0]],
            [path_with_path_choice_predicate],
            {"from": self.player},
        )
        self.assertEqual(
            self.gofp.get_path_choice(
                session_id, token_ids[0], stage_with_path_choice_predicate
            ),
            path_with_path_choice_predicate,
        )

        # Second Token
        self.gofp.stake_tokens_into_session(
            session_id, [token_ids[1]], {"from": self.player}
        )
        check_1 = self.gofp.call_path_choice_predicate(
            (
                session_id,
                stage_with_path_choice_predicate,
                path_with_path_choice_predicate,
            ),
            self.player.address,
            token_ids[1],
        )
        self.assertFalse(check_1)

        # With two tokens staked predicate should fail
        with self.assertRaises(VirtualMachineError):
            self.gofp.choose_current_stage_paths(
                session_id,
                [token_ids[1]],
                [path_with_path_choice_predicate],
                {"from": self.player},
            )
        self.assertEqual(
            self.gofp.get_path_choice(
                session_id, token_ids[1], stage_with_path_choice_predicate
            ),
            0,
        )

        # A path without a predicate can still be selected.
        self.gofp.choose_current_stage_paths(
            session_id,
            [token_ids[1]],
            [path_without_predicate],
            {"from": self.player},
        )
        self.assertEqual(
            self.gofp.get_path_choice(
                session_id, token_ids[1], stage_with_path_choice_predicate
            ),
            path_without_predicate,
        )


if __name__ == "__main__":
    unittest.main()
