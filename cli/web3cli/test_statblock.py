import unittest

from brownie import accounts, network, web3 as web3_client
from brownie.exceptions import VirtualMachineError
from moonworm.watch import _fetch_events_chunk

from . import (
    MockErc20,
    MockERC721,
    MockERC1155,
    MockTerminus,
    StatBlock,
    statblock_events,
)

MAX_UINT = 2**256 - 1


class StatBlockTests(unittest.TestCase):
    """
    StatBlockTests is the full suite of tests for the reference implementation of StatBlock.

    To test a custom StatBlock implementation, inherit from this class and modify the setup_permissions
    and setup_statblock methods to deploy that StatBlock implementation.
    """

    @classmethod
    def setup_statblock(cls):
        """
        Deploys the StatBlock contract being tested.
        """
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

        cls.statblock = StatBlock.StatBlock(None)
        cls.statblock.deploy(
            cls.terminus.address,
            cls.admin_terminus_pool_id,
            cls.deployer_txconfig,
        )

    @classmethod
    def setup_permissions(cls):
        """
        Grants administrator permissions to the administrator account.
        """
        cls.terminus.mint(
            cls.administrator.address,
            cls.admin_terminus_pool_id,
            1,
            "",
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

        cls.setup_statblock()
        cls.setup_permissions()

        cls.erc20_contract = MockErc20.MockErc20(None)
        cls.erc20_contract.deploy("ERC20 Token", "ERC20", cls.deployer_txconfig)

        cls.erc721_contract = MockERC721.MockERC721(None)
        cls.erc721_contract.deploy(cls.deployer_txconfig)

        cls.erc1155_contract = MockERC1155.MockERC1155(None)
        cls.erc1155_contract.deploy(cls.deployer_txconfig)

    def test_stat_block_version(self):
        self.assertEqual(self.statblock.stat_block_version(), "0.0.1")

    def test_admin_can_create_stat(self):
        """
        Tests that an administrator can create stats on a StatBlock contract.

        Tests:
        - createStat
        - NumStats
        - describeStat
        """
        num_stats_0 = self.statblock.num_stats()
        stat_name = f"stat_{num_stats_0 + 1}"
        tx_receipt = self.statblock.create_stat(stat_name, {"from": self.administrator})
        num_stats_1 = self.statblock.num_stats()

        self.assertEqual(num_stats_1, num_stats_0 + 1)

        stat_description = self.statblock.describe_stat(num_stats_1)
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
        self.assertEqual(event["args"]["statID"], num_stats_1)
        self.assertEqual(event["address"], self.statblock.address)

        stat_descriptor_updated_events = _fetch_events_chunk(
            web3_client,
            statblock_events.STAT_DESCRIPTOR_UPDATED_ABI,
            tx_receipt.block_number,
            tx_receipt.block_number,
        )
        self.assertEqual(len(stat_descriptor_updated_events), 1)

        stat_descriptor_updated_event = stat_descriptor_updated_events[0]
        self.assertEqual(
            stat_descriptor_updated_event["event"], "StatDescriptorUpdated"
        )
        self.assertEqual(stat_descriptor_updated_event["args"]["statID"], num_stats_1)
        self.assertEqual(stat_descriptor_updated_event["args"]["descriptor"], stat_name)
        self.assertEqual(
            stat_descriptor_updated_event["address"], self.statblock.address
        )

    def test_nonadmin_cannot_create_stat(self):
        """
        Tests that an account which is not a StatBlock administrator cannot create a stat on the StatBlock
        contract.

        Tests:
        - createStat
        - NumStats
        """
        # Test that player account does not own administrator badges.
        self.assertEqual(
            self.terminus.balance_of(self.player.address, self.admin_terminus_pool_id),
            0,
        )

        num_stats_0 = self.statblock.num_stats()
        stat_name = f"stat_{num_stats_0}"
        with self.assertRaises(VirtualMachineError):
            self.statblock.create_stat(stat_name, {"from": self.player})
        num_stats_1 = self.statblock.num_stats()
        self.assertEqual(num_stats_1, num_stats_0)

    def test_admin_can_set_stat_descriptor(self):
        """
        Tests that an administrator can modify stat descriptors.

        Note that since the stat does not have to be created before its descriptor is set, this test
        works with a stat that does not yet exist.

        It then creates the stat and checks that the stat descriptor was updated from the createStat
        call, too.

        Tests:
        - setStatDescriptor
        - createStat
        - describeStat
        """
        num_stats = self.statblock.num_stats()
        nonexistent_stat_id = num_stats + 1

        expected_stat_descriptor = "nonexistent_stat"

        tx_receipt_0 = self.statblock.set_stat_descriptor(
            nonexistent_stat_id, expected_stat_descriptor, {"from": self.administrator}
        )

        actual_stat_descriptor = self.statblock.describe_stat(nonexistent_stat_id)
        self.assertEqual(actual_stat_descriptor, expected_stat_descriptor)

        stat_descriptor_updated_events_0 = _fetch_events_chunk(
            web3_client,
            statblock_events.STAT_DESCRIPTOR_UPDATED_ABI,
            tx_receipt_0.block_number,
            tx_receipt_0.block_number,
        )
        self.assertEqual(len(stat_descriptor_updated_events_0), 1)

        stat_descriptor_updated_event_0 = stat_descriptor_updated_events_0[0]
        self.assertEqual(
            stat_descriptor_updated_event_0["event"], "StatDescriptorUpdated"
        )
        self.assertEqual(
            stat_descriptor_updated_event_0["args"]["statID"], nonexistent_stat_id
        )
        self.assertEqual(
            stat_descriptor_updated_event_0["args"]["descriptor"],
            expected_stat_descriptor,
        )
        self.assertEqual(
            stat_descriptor_updated_event_0["address"], self.statblock.address
        )

        expected_new_descriptor = f"stat_{nonexistent_stat_id}"

        tx_receipt_1 = self.statblock.create_stat(
            expected_new_descriptor, {"from": self.administrator}
        )

        actual_new_descriptor = self.statblock.describe_stat(nonexistent_stat_id)
        self.assertEqual(actual_new_descriptor, expected_new_descriptor)

        stat_descriptor_updated_events_1 = _fetch_events_chunk(
            web3_client,
            statblock_events.STAT_DESCRIPTOR_UPDATED_ABI,
            tx_receipt_1.block_number,
            tx_receipt_1.block_number,
        )
        self.assertEqual(len(stat_descriptor_updated_events_1), 1)

        stat_descriptor_updated_event_1 = stat_descriptor_updated_events_1[0]
        self.assertEqual(
            stat_descriptor_updated_event_1["event"], "StatDescriptorUpdated"
        )
        self.assertEqual(
            stat_descriptor_updated_event_1["args"]["statID"], nonexistent_stat_id
        )
        self.assertEqual(
            stat_descriptor_updated_event_1["args"]["descriptor"],
            expected_new_descriptor,
        )
        self.assertEqual(
            stat_descriptor_updated_event_1["address"], self.statblock.address
        )

    def test_nonadmin_cannot_set_stat_descriptor(self):
        """
        Tests that a non-administrator cannot modify stat descriptors.

        Checks with both non-existent and existent stats.

        Tests:
        - setStatDescriptor
        """
        num_stats = self.statblock.num_stats()
        nonexistent_stat_id = num_stats + 1

        attempted_stat_descriptor = "nonexistent_stat"

        with self.assertRaises(VirtualMachineError):
            self.statblock.set_stat_descriptor(
                nonexistent_stat_id, attempted_stat_descriptor, {"from": self.player}
            )

        actual_stat_descriptor = self.statblock.describe_stat(nonexistent_stat_id)
        self.assertEqual(actual_stat_descriptor, "")

        stat_name = f"stat_{nonexistent_stat_id}"
        self.statblock.create_stat(stat_name, {"from": self.administrator})
        actual_new_descriptor = self.statblock.describe_stat(nonexistent_stat_id)
        self.assertEqual(actual_new_descriptor, stat_name)

        with self.assertRaises(VirtualMachineError):
            self.statblock.set_stat_descriptor(
                nonexistent_stat_id, attempted_stat_descriptor, {"from": self.player}
            )

    def test_admin_can_assign_stats(self):
        """
        Tests that administrator can assign a set of stats to a token.

        Also tests that batchGetStats calls are consistent with return values of multiple getStats calls.

        Tests:
        - createStat
        - NumStats
        - assignStats
        - getStats
        - batchGetStats
        """
        # Setup phase: create the stats that we will assign to.
        num_assignable_stats = 3
        num_stats_0 = self.statblock.num_stats()

        stat_ids = [
            i + 1 for i in range(num_stats_0, num_stats_0 + num_assignable_stats)
        ]

        for i in stat_ids:
            stat_name = f"stat_{i}"
            self.statblock.create_stat(stat_name, {"from": self.administrator})

        num_stats_1 = self.statblock.num_stats()
        self.assertEqual(num_stats_1, num_stats_0 + num_assignable_stats)

        # Assign stats to ERC20 token. This is done by using 0 as the token_id.
        expected_erc20_stats = [20 + i for i in stat_ids]
        tx_receipt_0 = self.statblock.assign_stats(
            self.erc20_contract.address,
            0,
            stat_ids,
            expected_erc20_stats,
            {"from": self.administrator},
        )

        # Assign stats to ERC721 token. The token need not yet be minted.
        erc721_token_id = 42
        expected_erc721_stats = [721 + 42 + i for i in stat_ids]
        tx_receipt_1 = self.statblock.assign_stats(
            self.erc721_contract.address,
            erc721_token_id,
            stat_ids,
            expected_erc721_stats,
            {"from": self.administrator},
        )

        # Assign stats to ERC1155 tokens by token_id.
        erc1155_token_id = 1337
        expected_erc1155_stats = [1155 + 1337 + i for i in stat_ids]
        tx_receipt_2 = self.statblock.assign_stats(
            self.erc1155_contract.address,
            erc1155_token_id,
            stat_ids,
            expected_erc1155_stats,
            {"from": self.administrator},
        )

        # Check for StatAssigned event emissions.
        stat_assigned_events = _fetch_events_chunk(
            web3_client,
            statblock_events.STAT_ASSIGNED_ABI,
            tx_receipt_0.block_number,
            tx_receipt_2.block_number,
        )

        self.assertEqual(len(stat_assigned_events), 3 * num_assignable_stats)

        for i in range(num_assignable_stats):
            self.assertEqual(stat_assigned_events[i]["event"], "StatAssigned")
            self.assertEqual(
                stat_assigned_events[i]["args"]["tokenAddress"],
                self.erc20_contract.address,
            )
            self.assertEqual(stat_assigned_events[i]["args"]["tokenID"], 0)
            self.assertEqual(stat_assigned_events[i]["args"]["statID"], stat_ids[i])
            self.assertEqual(
                stat_assigned_events[i]["args"]["value"], expected_erc20_stats[i]
            )

        for i in range(num_assignable_stats):
            self.assertEqual(
                stat_assigned_events[num_assignable_stats + i]["event"], "StatAssigned"
            )
            self.assertEqual(
                stat_assigned_events[num_assignable_stats + i]["args"]["tokenAddress"],
                self.erc721_contract.address,
            )
            self.assertEqual(
                stat_assigned_events[num_assignable_stats + i]["args"]["tokenID"],
                erc721_token_id,
            )
            self.assertEqual(
                stat_assigned_events[num_assignable_stats + i]["args"]["statID"],
                stat_ids[i],
            )
            self.assertEqual(
                stat_assigned_events[num_assignable_stats + i]["args"]["value"],
                expected_erc721_stats[i],
            )

        for i in range(num_assignable_stats):
            self.assertEqual(
                stat_assigned_events[2 * num_assignable_stats + i]["event"],
                "StatAssigned",
            )
            self.assertEqual(
                stat_assigned_events[2 * num_assignable_stats + i]["args"][
                    "tokenAddress"
                ],
                self.erc1155_contract.address,
            )
            self.assertEqual(
                stat_assigned_events[2 * num_assignable_stats + i]["args"]["tokenID"],
                erc1155_token_id,
            )
            self.assertEqual(
                stat_assigned_events[2 * num_assignable_stats + i]["args"]["statID"],
                stat_ids[i],
            )
            self.assertEqual(
                stat_assigned_events[2 * num_assignable_stats + i]["args"]["value"],
                expected_erc1155_stats[i],
            )

        # Get stats and make sure they are correct
        actual_erc20_stats = self.statblock.get_stats(
            self.erc20_contract.address, 0, stat_ids
        )
        self.assertEqual(actual_erc20_stats, tuple(expected_erc20_stats))

        actual_erc721_stats = self.statblock.get_stats(
            self.erc721_contract.address, erc721_token_id, stat_ids
        )
        self.assertEqual(actual_erc721_stats, tuple(expected_erc721_stats))

        actual_erc1155_stats = self.statblock.get_stats(
            self.erc1155_contract.address, erc1155_token_id, stat_ids
        )
        self.assertEqual(actual_erc1155_stats, tuple(expected_erc1155_stats))

        # Test getting stats in a batch
        stats_batch = self.statblock.batch_get_stats(
            [
                self.erc20_contract.address,
                self.erc721_contract.address,
                self.erc1155_contract.address,
            ],
            [0, erc721_token_id, erc1155_token_id],
            stat_ids,
        )
        # Check for consistency with outputs of `getStats` for each `(tokenAddress, tokenID)` pair.
        self.assertEqual(stats_batch[0], tuple(actual_erc20_stats))
        self.assertEqual(stats_batch[1], tuple(actual_erc721_stats))
        self.assertEqual(stats_batch[2], tuple(actual_erc1155_stats))

    def test_admin_can_batch_assign_stats(self):
        """
        Tests that administrator can assign a set of stats to multiple tokens in a single transaction.

        Tests:
        - createStat
        - NumStats
        - batchAssignStats
        - getStats
        """
        # Setup phase: create the stats that we will assign to.
        num_assignable_stats = 3
        num_stats_0 = self.statblock.num_stats()

        stat_ids = [
            i + 1 for i in range(num_stats_0, num_stats_0 + num_assignable_stats)
        ]

        for i in stat_ids:
            stat_name = f"stat_{i}"
            self.statblock.create_stat(stat_name, {"from": self.administrator})

        num_stats_1 = self.statblock.num_stats()
        self.assertEqual(num_stats_1, num_stats_0 + num_assignable_stats)

        # Assign stats to ERC20, ERC721, and ERC1155 tokens all in one transaction.
        erc721_token_id = 42
        erc1155_token_id = 1337

        expected_erc20_stats = [20 + i for i in stat_ids]
        expected_erc721_stats = [721 + 42 + i for i in stat_ids]
        expected_erc1155_stats = [1155 + 1337 + i for i in stat_ids]

        tx_receipt = self.statblock.batch_assign_stats(
            [
                self.erc20_contract.address,
                self.erc721_contract.address,
                self.erc1155_contract.address,
            ],
            [0, erc721_token_id, erc1155_token_id],
            [stat_ids, stat_ids, stat_ids],
            [expected_erc20_stats, expected_erc721_stats, expected_erc1155_stats],
            {"from": self.administrator},
        )

        # Check for StatAssigned event emissions.
        stat_assigned_events = _fetch_events_chunk(
            web3_client,
            statblock_events.STAT_ASSIGNED_ABI,
            tx_receipt.block_number,
            tx_receipt.block_number,
        )

        self.assertEqual(len(stat_assigned_events), 3 * num_assignable_stats)

        for i in range(num_assignable_stats):
            self.assertEqual(stat_assigned_events[i]["event"], "StatAssigned")
            self.assertEqual(
                stat_assigned_events[i]["args"]["tokenAddress"],
                self.erc20_contract.address,
            )
            self.assertEqual(stat_assigned_events[i]["args"]["tokenID"], 0)
            self.assertEqual(stat_assigned_events[i]["args"]["statID"], stat_ids[i])
            self.assertEqual(
                stat_assigned_events[i]["args"]["value"], expected_erc20_stats[i]
            )

        for i in range(num_assignable_stats):
            self.assertEqual(
                stat_assigned_events[num_assignable_stats + i]["event"], "StatAssigned"
            )
            self.assertEqual(
                stat_assigned_events[num_assignable_stats + i]["args"]["tokenAddress"],
                self.erc721_contract.address,
            )
            self.assertEqual(
                stat_assigned_events[num_assignable_stats + i]["args"]["tokenID"],
                erc721_token_id,
            )
            self.assertEqual(
                stat_assigned_events[num_assignable_stats + i]["args"]["statID"],
                stat_ids[i],
            )
            self.assertEqual(
                stat_assigned_events[num_assignable_stats + i]["args"]["value"],
                expected_erc721_stats[i],
            )

        for i in range(num_assignable_stats):
            self.assertEqual(
                stat_assigned_events[2 * num_assignable_stats + i]["event"],
                "StatAssigned",
            )
            self.assertEqual(
                stat_assigned_events[2 * num_assignable_stats + i]["args"][
                    "tokenAddress"
                ],
                self.erc1155_contract.address,
            )
            self.assertEqual(
                stat_assigned_events[2 * num_assignable_stats + i]["args"]["tokenID"],
                erc1155_token_id,
            )
            self.assertEqual(
                stat_assigned_events[2 * num_assignable_stats + i]["args"]["statID"],
                stat_ids[i],
            )
            self.assertEqual(
                stat_assigned_events[2 * num_assignable_stats + i]["args"]["value"],
                expected_erc1155_stats[i],
            )

        # Get stats and make sure they are correct
        actual_erc20_stats = self.statblock.get_stats(
            self.erc20_contract.address, 0, stat_ids
        )
        self.assertEqual(actual_erc20_stats, tuple(expected_erc20_stats))

        actual_erc721_stats = self.statblock.get_stats(
            self.erc721_contract.address, erc721_token_id, stat_ids
        )
        self.assertEqual(actual_erc721_stats, tuple(expected_erc721_stats))

        actual_erc1155_stats = self.statblock.get_stats(
            self.erc1155_contract.address, erc1155_token_id, stat_ids
        )
        self.assertEqual(actual_erc1155_stats, tuple(expected_erc1155_stats))

    def test_nonadmin_cannot_assign_stats(self):
        """
        Tests that a non-administrator cannot assign stats to tokens.

        Tests:
        - assignStats

        Uses:
        - createStat
        - getStats
        """
        num_assignable_stats = 3
        num_stats_0 = self.statblock.num_stats()

        stat_ids = [
            i + 1 for i in range(num_stats_0, num_stats_0 + num_assignable_stats)
        ]

        for i in stat_ids:
            stat_name = f"stat_{i}"
            self.statblock.create_stat(stat_name, {"from": self.administrator})

        num_stats_1 = self.statblock.num_stats()
        self.assertEqual(num_stats_1, num_stats_0 + num_assignable_stats)

        erc721_token_id = 43
        expected_erc721_stats = [721 + erc721_token_id + i for i in stat_ids]

        expected_erc721_stats = self.statblock.get_stats(
            self.erc721_contract.address, erc721_token_id, stat_ids
        )

        with self.assertRaises(VirtualMachineError):
            self.statblock.assign_stats(
                self.erc721_contract.address,
                erc721_token_id,
                stat_ids,
                expected_erc721_stats,
                {"from": self.player},
            )

        actual_erc721_stats = self.statblock.get_stats(
            self.erc721_contract.address, erc721_token_id, stat_ids
        )
        self.assertEqual(actual_erc721_stats, expected_erc721_stats)

    def test_nonadmin_cannot_batch_assign_stats(self):
        """
        Tests that a non-administrator cannot assign stats to tokens in a batch.

        Tests:
        - batchAssignStats

        Uses:
        - createStat
        - getStats
        """
        num_assignable_stats = 3
        num_stats_0 = self.statblock.num_stats()

        stat_ids = [
            i + 1 for i in range(num_stats_0, num_stats_0 + num_assignable_stats)
        ]

        for i in stat_ids:
            stat_name = f"stat_{i}"
            self.statblock.create_stat(stat_name, {"from": self.administrator})

        num_stats_1 = self.statblock.num_stats()
        self.assertEqual(num_stats_1, num_stats_0 + num_assignable_stats)

        erc721_token_id = 44
        expected_erc721_stats = [721 + erc721_token_id + i for i in stat_ids]

        expected_erc721_stats = self.statblock.get_stats(
            self.erc721_contract.address, erc721_token_id, stat_ids
        )

        with self.assertRaises(VirtualMachineError):
            self.statblock.batch_assign_stats(
                [self.erc721_contract.address],
                [erc721_token_id],
                [stat_ids],
                [expected_erc721_stats],
                {"from": self.player},
            )

        actual_erc721_stats = self.statblock.get_stats(
            self.erc721_contract.address, erc721_token_id, stat_ids
        )
        self.assertEqual(actual_erc721_stats, expected_erc721_stats)


if __name__ == "__main__":
    unittest.main()
