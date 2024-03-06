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

        cls.player_1 = accounts[2]

        cls.random_person = accounts[3]
        cls.random_person_tx_config = {"from": cls.random_person}

        cls.player_2 = accounts[4]
        cls.player_3 = accounts[5]

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

    def test_admin_can_batch_mint(self):
        # Mint token to player
        player_balance_0 = self.nft.balance_of(self.player_1.address)
        token_id = self.nft.total_supply() + 1
        self.nft.mint(self.player_1.address, token_id, self.owner_tx_config)
        player_balance_1 = self.nft.balance_of(self.player_1.address)

        self.assertEqual(player_balance_1, player_balance_0 + 1)

        # Create slot
        metadata_uri = "http://www.example.com/test_achievement_1"
        self.achievement.create_achievement_slot(metadata_uri, self.admin_tx_config)
        achievement_pool = self.terminus.total_pools()

        self.assertEqual(self.terminus.uri(achievement_pool), metadata_uri)

        #  Batch mint 1 achievement
        self.assertEqual(self.terminus.balance_of(self.achievement.address, achievement_pool), 0)

        self.achievement.admin_batch_mint_to_inventory([token_id], [achievement_pool], self.admin_tx_config)

        self.assertEqual(self.terminus.balance_of(self.achievement.address, achievement_pool), 1)
        equipped_item = self.achievement.get_equipped_item(token_id, achievement_pool)

        # EquippedItem is (ItemType, ItemAddress, ItemTokenID, Amount)
        self.assertEqual(equipped_item, (1155, self.achievement.address, achievement_pool, 1))

    def test_non_admin_cannot_batch_mint(self):
        # Mint token to player
        player_balance_0 = self.nft.balance_of(self.player_1.address)
        token_id = self.nft.total_supply() + 1
        self.nft.mint(self.player_1.address, token_id, self.owner_tx_config)
        player_balance_1 = self.nft.balance_of(self.player_1.address)

        self.assertEqual(player_balance_1, player_balance_0 + 1)

        # Create slot
        metadata_uri = "http://www.example.com/test_achievement_2"
        self.achievement.create_achievement_slot(metadata_uri, self.admin_tx_config)
        achievement_pool = self.terminus.total_pools()

        self.assertEqual(self.terminus.uri(achievement_pool), metadata_uri)

        # Attempt batch mint
        with self.assertRaises(VirtualMachineError):
            self.achievement.admin_batch_mint_to_inventory([token_id], [achievement_pool], self.random_person_tx_config)
            
    def test_admin_can_mint_multiple_achievements_to_multiple_players(self):
        # Mint tokens to 3 players
        last_token_id = self.nft.total_supply()
        player_list = [self.player_1, self.player_2, self.player_3]
        player_balances_0 = list(map(lambda x: self.nft.balance_of(x), player_list))
        token_id_list = []
        for i, player in enumerate(player_list):
            token_id = last_token_id + i + 1
            self.nft.mint(player.address, last_token_id + i + 1, self.owner_tx_config)
            token_id_list.append(token_id)

        self.assertEqual(token_id_list, [last_token_id + 1, last_token_id + 2, last_token_id + 3])
        player_balances_1 = list(map(lambda x: self.nft.balance_of(x), player_list))
        self.assertEqual(player_balances_1, list(map(lambda x: x + 1, player_balances_0)))

        # Create 2 slots
        metadata_uri_1 = "http://www.example.com/test_achievement_3"
        self.achievement.create_achievement_slot(metadata_uri_1, self.admin_tx_config)
        achievement_pool_1 = self.terminus.total_pools()

        self.assertEqual(self.terminus.uri(achievement_pool_1), metadata_uri_1)

        metadata_uri_2 = "http://www.example.com/test_achievement_3"
        self.achievement.create_achievement_slot(metadata_uri_2, self.admin_tx_config)
        achievement_pool_2 = self.terminus.total_pools()

        self.assertEqual(self.terminus.uri(achievement_pool_2), metadata_uri_2)

        # Batch mint achievements to players
        self.assertEqual(self.terminus.balance_of(self.achievement.address, achievement_pool_1), 0)
        self.assertEqual(self.terminus.balance_of(self.achievement.address, achievement_pool_2), 0)

        double_token_list = token_id_list + token_id_list
        achievement_list = [achievement_pool_1] * 3 + [achievement_pool_2] * 3
        self.achievement.admin_batch_mint_to_inventory(double_token_list, achievement_list, self.admin_tx_config)

        self.assertEqual(self.terminus.balance_of(self.achievement.address, achievement_pool_1), 3)
        self.assertEqual(self.terminus.balance_of(self.achievement.address, achievement_pool_2), 3)

        for token_id in token_id_list:
            equipped_item_1 = self.achievement.get_equipped_item(token_id, achievement_pool_1)

            # EquippedItem is (ItemType, ItemAddress, ItemTokenID, Amount)
            self.assertEqual(equipped_item_1, (1155, self.achievement.address, achievement_pool_1, 1))

            equipped_item_2 = self.achievement.get_equipped_item(token_id, achievement_pool_2)

            # EquippedItem is (ItemType, ItemAddress, ItemTokenID, Amount)
            self.assertEqual(equipped_item_2, (1155, self.achievement.address, achievement_pool_2, 1))


