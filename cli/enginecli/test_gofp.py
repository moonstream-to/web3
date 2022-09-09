import unittest

from brownie import accounts, network

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

        cls.terminus.mint(
            cls.owner.address, cls.admin_pool_id, 1, "", cls.owner_tx_config
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

        actual_payment_amount = 42
        actual_uri = (
            "https://example.com/test_create_session_then_get_session_active.json"
        )
        actual_stages = (5, 5, 3, 3, 2)
        actual_is_active = True

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            actual_payment_amount,
            actual_uri,
            actual_stages,
            actual_is_active,
            self.owner_tx_config,
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
        self.assertEqual(payment_amount, actual_payment_amount)
        self.assertTrue(actual_is_active)
        self.assertEqual(uri, actual_uri)
        self.assertEqual(stages, actual_stages)
        self.assertEqual(correct_path, tuple([0 for _ in actual_stages]))

    def test_create_session_then_get_session_inactive(self):
        num_sessions_0 = self.gofp.num_sessions()

        actual_payment_amount = 43
        actual_uri = (
            "https://example.com/test_create_session_then_get_session_inactive.json"
        )
        actual_stages = (5, 5, 3)
        actual_is_active = False

        self.gofp.create_session(
            self.nft.address,
            self.payment_token.address,
            actual_payment_amount,
            actual_uri,
            actual_stages,
            actual_is_active,
            self.owner_tx_config,
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
        self.assertEqual(payment_amount, actual_payment_amount)
        self.assertFalse(actual_is_active)
        self.assertEqual(uri, actual_uri)
        self.assertEqual(stages, actual_stages)
        self.assertEqual(correct_path, tuple([0 for _ in actual_stages]))


if __name__ == "__main__":
    unittest.main()
