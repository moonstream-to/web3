import unittest

from brownie import accounts, network, web3 as web3_client, ZERO_ADDRESS
from brownie.exceptions import VirtualMachineError
from moonworm.watch import _fetch_events_chunk

from . import GOFPFacet, MockTerminus, MockErc20, MockERC721
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
    ],
    "name": "SessionCreated",
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
        ) = session

        self.assertEqual(nft_address, self.nft.address)
        self.assertEqual(payment_address, self.payment_token.address)
        self.assertEqual(payment_amount, expected_payment_amount)
        self.assertTrue(is_active)
        self.assertEqual(uri, expected_uri)
        self.assertEqual(stages, expected_stages)
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
        ) = session

        self.assertEqual(nft_address, self.nft.address)
        self.assertEqual(payment_address, self.payment_token.address)
        self.assertEqual(payment_amount, expected_payment_amount)
        self.assertFalse(is_active)
        self.assertEqual(uri, expected_uri)
        self.assertEqual(stages, expected_stages)
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
                {"from": self.game_master},
            )

        self.gofp.create_session(
            self.nft.address,
            ZERO_ADDRESS,
            0,
            expected_is_active,
            expected_uri,
            expected_stages,
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
        ) = session

        self.assertEqual(nft_address, self.nft.address)
        self.assertEqual(payment_address, ZERO_ADDRESS)
        self.assertEqual(payment_amount, 0)
        self.assertFalse(is_active)
        self.assertEqual(uri, expected_uri)
        self.assertEqual(stages, expected_stages)
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
                {"from": self.owner},
            )

        num_sessions_1 = self.gofp.num_sessions()
        self.assertEqual(num_sessions_1, num_sessions_0)

    def test_create_session_fires_event(self):
        # TODO(zomglings): Move to top of file as a constant (see PATH_CHOSEN_EVENT_ABI)
        session_created_event_abi = {
            "anonymous": False,
            "inputs": [
                {
                    "indexed": False,
                    "internalType": "uint256",
                    "name": "sessionID",
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
                    "name": "URI",
                    "type": "string",
                },
                {
                    "indexed": False,
                    "internalType": "bool",
                    "name": "active",
                    "type": "bool",
                },
            ],
            "name": "SessionCreated",
            "type": "event",
        }

        expected_payment_amount = 60
        expected_uri = "https://example.com/test_create_session_fires_event.json"
        expected_stages = (5,)
        expected_is_active = True

        tx_receipt = self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            expected_payment_amount,
            expected_is_active,
            expected_uri,
            expected_stages,
            {"from": self.game_master},
        )

        events = _fetch_events_chunk(
            web3_client,
            SESSION_CREATED_EVENT_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )

        self.assertEqual(len(events), 1)

        self.assertEqual(events[0]["args"]["sessionId"], self.gofp.num_sessions())
        self.assertEqual(events[0]["args"]["playerTokenAddress"], self.nft.address)
        self.assertEqual(
            events[0]["args"]["paymentTokenAddress"], self.payment_token.address
        )
        self.assertEqual(events[0]["args"]["paymentAmount"], expected_payment_amount)
        self.assertEqual(events[0]["args"]["uri"], expected_uri)

    def test_can_change_session_is_active_as_game_master(self):
        payment_amount = 130
        uri = (
            "https://example.com/test_can_change_session_is_active_as_game_master.json"
        )
        stages = (5, 5, 3)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        _, _, _, is_active_0, _, _, _ = self.gofp.get_session(session_id)
        self.assertFalse(is_active_0)

        self.gofp.set_session_active(session_id, True, {"from": self.game_master})

        _, _, _, is_active_1, _, _, _ = self.gofp.get_session(session_id)
        self.assertTrue(is_active_1)

        self.gofp.set_session_active(session_id, False, {"from": self.game_master})

        _, _, _, is_active_2, _, _, _ = self.gofp.get_session(session_id)
        self.assertFalse(is_active_2)

        self.gofp.set_session_active(session_id, False, {"from": self.game_master})

        _, _, _, is_active_3, _, _, _ = self.gofp.get_session(session_id)
        self.assertFalse(is_active_3)

    def test_cannot_change_session_is_active_as_non_game_master(self):
        payment_amount = 131
        uri = "https://example.com/test_cannot_change_session_is_active_as_non_game_master.json"
        stages = (5, 5, 3)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        _, _, _, is_active_0, _, _, _ = self.gofp.get_session(session_id)
        self.assertFalse(is_active_0)

        with self.assertRaises(VirtualMachineError):
            self.gofp.set_session_active(session_id, True, {"from": self.player})

        _, _, _, is_active_1, _, _, _ = self.gofp.get_session(session_id)
        self.assertFalse(is_active_1)

        with self.assertRaises(VirtualMachineError):
            self.gofp.set_session_active(session_id, True, {"from": self.owner})

        _, _, _, is_active_2, _, _, _ = self.gofp.get_session(session_id)
        self.assertFalse(is_active_2)

        session_activated_event_abi = {
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

        payment_amount = 131
        uri = "https://example.com/test_set_session_active_fires_event.json"
        stages = (5,)
        is_active = True

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        tx_receipt = self.gofp.set_session_active(
            session_id, False, {"from": self.game_master}
        )

        events = _fetch_events_chunk(
            web3_client,
            session_activated_event_abi,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )

        self.assertEqual(len(events), 1)

        self.assertEqual(events[0]["args"]["sessionId"], self.gofp.num_sessions())
        self.assertFalse(events[0]["args"]["active"])

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
        # TODO(zomglings): Move to top of file as a constant (see PATH_CHOSEN_EVENT_ABI)
        path_registered_event_abi = {
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
            path_registered_event_abi,
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

        self.gofp.set_stage_rewards(
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

    def test_player_cannot_unstake_from_active_session(self):
        payment_amount = 135
        uri = "https://example.com/test_player_cannot_unstake_from_active_session.json"
        stages = (5, 5, 3)
        is_active = True

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
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

        self.gofp.set_session_active(session_id, True, {"from": self.game_master})

        unstaked_token_ids = [token_ids[i] for i in range(1, len(token_ids) - 1)]

        with self.assertRaises(VirtualMachineError):
            self.gofp.unstake_tokens_from_session(
                session_id, unstaked_token_ids, {"from": self.player}
            )

        num_staked_2 = self.gofp.num_tokens_staked_into_session(
            session_id, self.player.address
        )
        num_owned_by_player_2 = self.nft.balance_of(self.player.address)
        num_owned_by_contract_2 = self.nft.balance_of(self.gofp.address)

        self.assertEqual(num_staked_2, num_staked_1)
        self.assertEqual(num_owned_by_player_2, num_owned_by_player_1)
        self.assertEqual(num_owned_by_contract_2, num_owned_by_contract_1)

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


class TestFullGames(GOFPTestCase):
    def test_single_player_game(self):
        payment_amount = 337
        uri = "https://example.com/test_single_player_game.json"
        # NOTE: The test assumes that there are 3 stages. You can change the number of paths per change,
        # but do not change the number of stages.
        # The stage numbers also need to be coprime to each other - Chinese Remainder Theorem!
        stages = (2, 3, 5)
        correct_paths = (2, 1, 3)
        is_active = True

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            is_active,
            uri,
            stages,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

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

        self.gofp.choose_current_stage_paths(
            session_id,
            token_ids,
            first_stage_path_choices,
            {"from": self.player},
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

        self.gofp.set_session_choosing_active(
            session_id, False, {"from": self.game_master}
        )
        self.gofp.set_correct_path_for_stage(
            session_id, 3, correct_paths[2], True, {"from": self.game_master}
        )

        # Check that current stage has progressed to stage 4
        self.assertEqual(self.gofp.get_current_stage(session_id), 4)

        for token_id in token_ids:
            if token_id not in third_stage_correct_token_ids:
                with self.assertRaises(VirtualMachineError):
                    self.gofp.choose_current_stage_paths(
                        session_id,
                        [token_id],
                        [1],
                        {"from": self.player},
                    )


if __name__ == "__main__":
    unittest.main()
