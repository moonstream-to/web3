import unittest

from brownie import accounts, network, web3 as web3_client
from brownie.exceptions import VirtualMachineError
from moonworm.watch import _fetch_events_chunk

from . import GOFPFacet, MockTerminus, MockErc20, MockERC721
from .core import gofp_gogogo


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

        # It is important for some of the tests that the owner of the contract *not* be the game master.
        cls.terminus.mint(
            cls.game_master.address, cls.admin_pool_id, 1, "", cls.owner_tx_config
        )

        cls.deployed_contracts = gofp_gogogo(
            cls.terminus.address, cls.admin_pool_id, cls.owner_tx_config
        )
        cls.gofp = GOFPFacet.GOFPFacet(cls.deployed_contracts["contracts"]["Diamond"])

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
            expected_uri,
            expected_stages,
            expected_is_active,
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
            uri,
            stages,
            correct_path,
        ) = session

        self.assertEqual(nft_address, self.nft.address)
        self.assertEqual(payment_address, self.payment_token.address)
        self.assertEqual(payment_amount, expected_payment_amount)
        self.assertTrue(is_active)
        self.assertEqual(uri, expected_uri)
        self.assertEqual(stages, expected_stages)
        self.assertEqual(correct_path, tuple([0 for _ in expected_stages]))

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
            expected_uri,
            expected_stages,
            expected_is_active,
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
            uri,
            stages,
            correct_path,
        ) = session

        self.assertEqual(nft_address, self.nft.address)
        self.assertEqual(payment_address, self.payment_token.address)
        self.assertEqual(payment_amount, expected_payment_amount)
        self.assertFalse(is_active)
        self.assertEqual(uri, expected_uri)
        self.assertEqual(stages, expected_stages)
        self.assertEqual(correct_path, tuple([0 for _ in expected_stages]))

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
                failed_uri,
                failed_stages,
                failed_is_active,
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
                failed_uri,
                failed_stages,
                failed_is_active,
                {"from": self.owner},
            )

        num_sessions_1 = self.gofp.num_sessions()
        self.assertEqual(num_sessions_1, num_sessions_0)

    def test_create_session_fires_event(self):
        session_created_event_abi = {
            "anonymous": False,
            "inputs": [
                {
                    "indexed": True,
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
                    "name": "uri",
                    "type": "string",
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
            expected_uri,
            expected_stages,
            expected_is_active,
            {"from": self.game_master},
        )

        events = _fetch_events_chunk(
            web3_client,
            session_created_event_abi,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )

        self.assertEqual(len(events), 1)

        self.assertEqual(events[0]["args"]["sessionID"], self.gofp.num_sessions())
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
            uri,
            stages,
            is_active,
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
            uri,
            stages,
            is_active,
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

    def test_set_session_active_fires_event(self):
        session_activated_event_abi = {
            "anonymous": False,
            "inputs": [
                {
                    "indexed": True,
                    "internalType": "uint256",
                    "name": "sessionID",
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
            uri,
            stages,
            is_active,
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

        self.assertEqual(events[0]["args"]["sessionID"], self.gofp.num_sessions())
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
            uri,
            stages,
            is_active,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # Paths can be registered out of order. In this test, we register paths for stages in the
        # following order:
        # Stage 1: Path 5
        # Stage 0: Path 1
        # Stage 2: Path 3
        self.gofp.register_path(session_id, 1, 5, {"from": self.game_master})
        _, _, _, _, _, _, paths_0 = self.gofp.get_session(session_id)
        self.assertEqual(paths_0, (0, 5, 0))

        self.gofp.register_path(session_id, 0, 1, {"from": self.game_master})
        _, _, _, _, _, _, paths_1 = self.gofp.get_session(session_id)
        self.assertEqual(paths_1, (1, 5, 0))

        self.gofp.register_path(session_id, 2, 3, {"from": self.game_master})
        _, _, _, _, _, _, paths_2 = self.gofp.get_session(session_id)
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
            uri,
            stages,
            is_active,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        with self.assertRaises(VirtualMachineError):
            self.gofp.register_path(session_id, 0, 1, {"from": self.player})
        _, _, _, _, _, _, paths_0 = self.gofp.get_session(session_id)
        self.assertEqual(paths_0, (0, 0, 0))

        with self.assertRaises(VirtualMachineError):
            self.gofp.register_path(session_id, 1, 5, {"from": self.owner})
        _, _, _, _, _, _, paths_1 = self.gofp.get_session(session_id)
        self.assertEqual(paths_1, (0, 0, 0))

        with self.assertRaises(VirtualMachineError):
            self.gofp.register_path(session_id, 2, 3, {"from": self.random_person})
        _, _, _, _, _, _, paths_2 = self.gofp.get_session(session_id)
        self.assertEqual(paths_2, (0, 0, 0))

    def test_game_master_cannot_register_invalid_path(self):
        payment_amount = 131
        uri = "https://example.com/test_game_master_cannot_register_invalid_path.json"
        stages = (5, 5, 3)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            uri,
            stages,
            is_active,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        # Invalid session
        with self.assertRaises(VirtualMachineError):
            self.gofp.register_path(session_id + 1, 1, 5, {"from": self.game_master})
        _, _, _, _, _, _, paths_0 = self.gofp.get_session(session_id)
        self.assertEqual(paths_0, (0, 0, 0))

        # Invalid stage
        with self.assertRaises(VirtualMachineError):
            self.gofp.register_path(session_id, 3, 1, {"from": self.game_master})
        _, _, _, _, _, _, paths_1 = self.gofp.get_session(session_id)
        self.assertEqual(paths_1, (0, 0, 0))

        # Path must be >= 1
        with self.assertRaises(VirtualMachineError):
            self.gofp.register_path(session_id, 0, 0, {"from": self.game_master})
        _, _, _, _, _, _, paths_1 = self.gofp.get_session(session_id)
        self.assertEqual(paths_1, (0, 0, 0))

        # Path must be <= number of choices for the given stage
        with self.assertRaises(VirtualMachineError):
            self.gofp.register_path(session_id, 0, 6, {"from": self.game_master})
        _, _, _, _, _, _, paths_1 = self.gofp.get_session(session_id)
        self.assertEqual(paths_1, (0, 0, 0))

    def test_game_master_cannot_register_path_multiple_times_for_same_stage(self):
        payment_amount = 131
        uri = "https://example.com/test_game_master_cannot_register_path_multiple_times_for_same_stage.json"
        stages = (5, 5, 3)
        is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            payment_amount,
            uri,
            stages,
            is_active,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        self.gofp.register_path(session_id, 1, 5, {"from": self.game_master})
        _, _, _, _, _, _, paths_0 = self.gofp.get_session(session_id)
        self.assertEqual(paths_0, (0, 5, 0))

        with self.assertRaises(VirtualMachineError):
            self.gofp.register_path(session_id, 1, 4, {"from": self.game_master})
        _, _, _, _, _, _, paths_1 = self.gofp.get_session(session_id)
        self.assertEqual(paths_1, (0, 5, 0))

        self.gofp.register_path(session_id, 2, 3, {"from": self.game_master})
        _, _, _, _, _, _, paths_2 = self.gofp.get_session(session_id)
        self.assertEqual(paths_2, (0, 5, 3))

    def test_register_path_fires_event(self):
        path_registered_event_abi = {
            "anonymous": False,
            "inputs": [
                {
                    "indexed": True,
                    "internalType": "uint256",
                    "name": "sessionID",
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
            uri,
            stages,
            is_active,
            {"from": self.game_master},
        )

        session_id = self.gofp.num_sessions()

        tx_receipt = self.gofp.register_path(
            session_id, 1, 5, {"from": self.game_master}
        )
        events = _fetch_events_chunk(
            web3_client,
            path_registered_event_abi,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )

        self.assertEqual(len(events), 1)

        self.assertEqual(events[0]["args"]["sessionID"], self.gofp.num_sessions())
        self.assertEqual(events[0]["args"]["stage"], 1)
        self.assertEqual(events[0]["args"]["path"], 5)


if __name__ == "__main__":
    unittest.main()
