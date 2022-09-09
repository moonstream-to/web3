import unittest

from brownie import accounts, network
from brownie.exceptions import VirtualMachineError

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


if __name__ == "__main__":
    unittest.main()
