import unittest

from brownie import accounts, network, web3 as web3_client
from brownie.exceptions import VirtualMachineError
from moonworm.watch import _fetch_events_chunk

from . import MockErc20, MockTerminus, StatBlock, statblock_events

MAX_UINT = 2**256 - 1


class StatBlockTests(unittest.TestCase):
    @classmethod
    def setup_permissions(cls):
        cls.terminus = MockTerminus.MockTerminus(None)
        cls.terminus.deploy(cls.deployer_txconfig)

        cls.payment_token = MockErc20.MockErc20(None)
        cls.payment_token.deploy("lol", "lol", cls.deployer_txconfig)

        cls.terminus.set_payment_token(cls.payment_token.address, cls.deployer_txconfig)
        cls.terminus.set_pool_base_price(1, cls.deployer_txconfig)

        cls.terminus.set_payment_token(cls.payment_token.address, cls.deployer_txconfig)
        cls.terminus.set_pool_base_price(1, cls.deployer_txconfig)

        cls.payment_token.mint(cls.deployer.address, 999999, cls.deployer_txconfig)
        cls.payment_token.approve(cls.terminus.address, MAX_UINT, cls.deployer_txconfig)

        cls.terminus.create_pool_v1(1, False, True, cls.deployer_txconfig)
        cls.admin_terminus_pool_id = cls.terminus.total_pools()

        cls.terminus.mint(
            cls.administrator.address,
            cls.admin_terminus_pool_id,
            1,
            "",
            cls.deployer_txconfig,
        )

    @classmethod
    def setup_statblock(cls):
        cls.statblock = StatBlock.StatBlock(None)
        cls.statblock.deploy(
            cls.terminus.address,
            cls.admin_terminus_pool_id,
            cls.deployer_txconfig,
        )

    @classmethod
    def setUpClass(cls):
        try:
            network.connect()
        except:
            pass

        cls.deployer = accounts[0]
        cls.deployer_txconfig = {"from": cls.deployer}

        cls.administrator = accounts[1]
        cls.player = accounts[2]
        cls.random_person = accounts[3]

        cls.setup_permissions()
        cls.setup_statblock()

    def test_admin_can_create_stat(self):
        """
        Tests that an administrator can create stats on a StatBlock contract.
        """
        num_stats_0 = self.statblock.num_stats()
        stat_name = f"stat_{num_stats_0}"
        tx_receipt = self.statblock.create_stat(stat_name, {"from": self.administrator})
        num_stats_1 = self.statblock.num_stats()

        self.assertEqual(num_stats_1, num_stats_0 + 1)

        stat_description = self.statblock.describe_stat(num_stats_0)
        self.assertEqual(stat_description, stat_name)

        stat_created_events = _fetch_events_chunk(
            web3_client,
            statblock_events.STAT_CREATED_ABI,
            tx_receipt.block_number,
            tx_receipt.block_number,
        )
        self.assertEqual(len(stat_created_events), 1)

        event = stat_created_events[0]
        self.assertEqual(event["event"], "StatCreated")
        self.assertEqual(event["args"]["statID"], num_stats_0)
        self.assertEqual(event["args"]["descriptor"], stat_name)
        self.assertEqual(event["address"], self.statblock.address)


if __name__ == "__main__":
    unittest.main()
