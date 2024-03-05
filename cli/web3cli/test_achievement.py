import unittest

from brownie import accounts, network, web3 as web3_client, ZERO_ADDRESS
from brownie.exceptions import VirtualMachineError
from brownie.network import chain
from moonworm.watch import _fetch_events_chunk

from . import AchievementFacet, MockERC721, MockTerminus, inventory_events
from .core import achievement_gogogo

MAX_UINT = 2**256 - 1


class AchievementTestCase(unittest.TestCase):
    @classmethod
    def deploy_achievement(cls) -> str:
        """
        Deploys an Achiement contract and returns the address.
        """
        deployed_contracts = achievement_gogogo(
            cls.nft.address,
            cls.owner_tx_config,
        )
        return deployed_contracts["contracts"]["Diamond"]

    @classmethod
    def setUpClass(cls) -> None:
        try:
            network.connect()
        except:
            pass

        cls.owner = accounts[0]
        cls.owner_tx_config = {"from": cls.owner}

        cls.admin = accounts[1]
        cls.admin_tx_config = {"from": cls.admin}

        cls.player = accounts[2]
        cls.player_tx_config = {"from": cls.player}

        cls.random_person = accounts[3]
        cls.random_person_tx_config = {"from": cls.random_person}

        cls.nft = MockERC721.MockERC721(None)
        cls.nft.deploy(cls.owner_tx_config)

        cls.item_nft = MockERC721.MockERC721(None)
        cls.item_nft.deploy(cls.owner_tx_config)

        cls.predeployment_block = len(chain)
        achievement_address = cls.deploy_achievement()
        cls.achievement = AchievementFacet.AchievementFacet(achievement_address)
        cls.postdeployment_block = len(chain)

        cls.terminus = MockTerminus.MockTerminus(achievement_address)

        cls.achievement.grant_admin_privilege(cls.admin.address, cls.owner_tx_config)


class AchievementSetupTests(AchievementTestCase):

    def test_admin_terminus_info(self):
        terminus_info = self.achievement.admin_terminus_info()
        self.assertEqual(terminus_info[0], self.achievement.address)

    def test_administrator_designated_event(self):
        terminus_info = self.achievement.admin_terminus_info()

        administrator_designated_events = _fetch_events_chunk(
            web3_client,
            inventory_events.ADMINISTRATOR_DESIGNATED_ABI,
            self.predeployment_block,
            self.postdeployment_block,
        )
        self.assertEqual(len(administrator_designated_events), 1)

        self.assertEqual(
            administrator_designated_events[0]["args"]["adminTerminusAddress"],
            terminus_info[0],
        )
        self.assertEqual(
            administrator_designated_events[0]["args"]["adminTerminusPoolId"],
            terminus_info[1],
        )

    def test_subject_erc721_address(self):
        self.assertEqual(self.achievement.subject(), self.nft.address)

    def test_contract_address_designated_event(self):
        contract_address_designated_events = _fetch_events_chunk(
            web3_client,
            inventory_events.NEW_SUBJECT_ADDRESS_ABI,
            self.predeployment_block,
            self.postdeployment_block,
        )
        self.assertEqual(len(contract_address_designated_events), 1)

        self.assertEqual(
            contract_address_designated_events[0]["args"]["contractAddress"],
            self.nft.address,
        )

    def test_grant_and_revoke_admin_privilege(self):
        (admin_terminus_addres, admin_terminus_pool_id) = self.achievement.admin_terminus_info()

        self.assertEqual(
            admin_terminus_addres,
            self.terminus.address
        )

        balance = self.terminus.balance_of(self.random_person.address, admin_terminus_pool_id)
        self.assertEqual(
            balance,
            0
        )

        self.achievement.grant_admin_privilege(self.random_person.address, self.owner_tx_config)

        balance = self.terminus.balance_of(self.random_person.address, admin_terminus_pool_id)
        self.assertEqual(
            balance,
            1
        )

        self.achievement.revoke_admin_privilege(self.random_person.address, self.owner_tx_config)

        balance = self.terminus.balance_of(self.random_person.address, admin_terminus_pool_id)
        self.assertEqual(
            balance,
            0
        )


class TestAdminFlow(AchievementTestCase):

    def test_admin_can_create_achievement_slot(self):

        metadata_uri = "http://www.example.com/test_achievement_1"

        initial_num_pools = self.terminus.total_pools()
        initial_num_slots = self.achievement.num_slots()


        self.assertEqual(initial_num_pools, initial_num_slots)

        self.achievement.create_achievement_slot(metadata_uri, self.admin_tx_config)

        final_num_pools = self.terminus.total_pools()
        final_num_slots = self.achievement.num_slots()

        self.assertEqual(
            final_num_pools,
            initial_num_pools + 1,
        )
        self.assertEqual(
            final_num_slots,
            initial_num_slots + 1,
        )
        self.assertEqual(final_num_pools, final_num_slots)
        self.assertEqual(
            self.terminus.uri(final_num_pools),
            metadata_uri
        )
        self.assertEqual(
            self.achievement.get_slot_uri(final_num_slots),
            metadata_uri
        )

    def test_non_admin_cannot_create_achievement_slot(self):

        metadata_uri = "http://www.example.com/test_achievement_1"

        initial_num_pools = self.terminus.total_pools()
        initial_num_slots = self.achievement.num_slots()


        self.assertEqual(initial_num_pools, initial_num_slots)

        with self.assertRaises(VirtualMachineError):
            self.achievement.create_achievement_slot(metadata_uri, self.random_person_tx_config)

        final_num_pools = self.terminus.total_pools()
        final_num_slots = self.achievement.num_slots()

        self.assertEqual(
            final_num_pools,
            initial_num_pools,
        )
        self.assertEqual(
            final_num_slots,
            initial_num_slots,
        )
        self.assertEqual(final_num_pools, final_num_slots)