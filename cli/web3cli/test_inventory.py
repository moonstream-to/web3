import unittest

from brownie import accounts, network, web3 as web3_client, ZERO_ADDRESS
from brownie.exceptions import VirtualMachineError
from brownie.network import chain
from moonworm.watch import _fetch_events_chunk

from . import InventoryFacet, MockErc20, MockERC721, MockTerminus, inventory_events
from .core import inventory_gogogo

MAX_UINT = 2**256 - 1


class InventoryTestCase(unittest.TestCase):
    @classmethod
    def deploy_inventory(cls) -> str:
        """
        Deploys an Inventory and returns the address of the deployed contract.
        """
        deployed_contracts = inventory_gogogo(
            cls.terminus.address,
            cls.admin_terminus_pool_id,
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
        cls.player = accounts[2]
        cls.random_person = accounts[3]

        cls.nft = MockERC721.MockERC721(None)
        cls.nft.deploy(cls.owner_tx_config)

        cls.item_nft = MockERC721.MockERC721(None)
        cls.item_nft.deploy(cls.owner_tx_config)

        cls.terminus = MockTerminus.MockTerminus(None)
        cls.terminus.deploy(cls.owner_tx_config)

        cls.payment_token = MockErc20.MockErc20(None)
        cls.payment_token.deploy("lol", "lol", cls.owner_tx_config)

        cls.terminus.set_payment_token(cls.payment_token.address, cls.owner_tx_config)
        cls.terminus.set_pool_base_price(1, cls.owner_tx_config)

        cls.payment_token.mint(cls.owner.address, 999999, cls.owner_tx_config)

        cls.payment_token.approve(cls.terminus.address, MAX_UINT, cls.owner_tx_config)

        cls.terminus.create_pool_v1(1, False, True, cls.owner_tx_config)
        cls.admin_terminus_pool_id = cls.terminus.total_pools()

        # Mint admin badge to administrator account
        cls.terminus.mint(
            cls.admin.address, cls.admin_terminus_pool_id, 1, "", cls.owner_tx_config
        )

        cls.predeployment_block = len(chain)
        inventory_address = cls.deploy_inventory()
        cls.inventory = InventoryFacet.InventoryFacet(inventory_address)
        cls.postdeployment_block = len(chain)


class InventorySetupTests(InventoryTestCase):
    def test_admin_terminus_info(self):
        terminus_info = self.inventory.admin_terminus_info()
        self.assertEqual(terminus_info[0], self.terminus.address)
        self.assertEqual(terminus_info[1], self.admin_terminus_pool_id)

    def test_administrator_designated_event(self):
        administrator_designated_events = _fetch_events_chunk(
            web3_client,
            inventory_events.ADMINISTRATOR_DESIGNATED_ABI,
            self.predeployment_block,
            self.postdeployment_block,
        )
        self.assertEqual(len(administrator_designated_events), 1)

        self.assertEqual(
            administrator_designated_events[0]["args"]["adminTerminusAddress"],
            self.terminus.address,
        )
        self.assertEqual(
            administrator_designated_events[0]["args"]["adminTerminusPoolId"],
            self.admin_terminus_pool_id,
        )

    def test_subject_erc721_address(self):
        self.assertEqual(self.inventory.subject(), self.nft.address)

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


class TestAdminFlow(InventoryTestCase):
    def test_admin_can_create_persistent_slot(self):
        persistent = True

        num_slots_0 = self.inventory.num_slots()
        tx_receipt = self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        num_slots_1 = self.inventory.num_slots()

        self.assertEqual(num_slots_1, num_slots_0 + 1)
        self.assertEqual(self.inventory.slot_is_persistent(num_slots_1), persistent)

        inventory_slot_created_events = _fetch_events_chunk(
            web3_client,
            inventory_events.SLOT_CREATED_ABI,
            tx_receipt.block_number,
            tx_receipt.block_number,
        )
        self.assertEqual(len(inventory_slot_created_events), 1)
        self.assertEqual(
            inventory_slot_created_events[0]["args"]["creator"],
            self.admin.address,
        )
        self.assertEqual(
            inventory_slot_created_events[0]["args"]["slot"],
            num_slots_1,
        )

        new_slot_uri_events = _fetch_events_chunk(
            web3_client,
            inventory_events.NEW_SLOT_URI_ABI,
            tx_receipt.block_number,
            tx_receipt.block_number,
        )
        self.assertEqual(len(new_slot_uri_events), 1)
        self.assertEqual(new_slot_uri_events[0]["args"]["slotId"], num_slots_1)

        new_slot_persistence_events = _fetch_events_chunk(
            web3_client,
            inventory_events.NEW_SLOT_PERSISTENCE_ABI,
            tx_receipt.block_number,
            tx_receipt.block_number,
        )
        self.assertEqual(len(new_slot_persistence_events), 1)
        self.assertEqual(new_slot_persistence_events[0]["args"]["slotId"], num_slots_1)
        self.assertEqual(
            new_slot_persistence_events[0]["args"]["persistent"], persistent
        )

    def test_admin_can_create_impersistent_slot(self):
        persistent = False

        num_slots_0 = self.inventory.num_slots()
        tx_receipt = self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        num_slots_1 = self.inventory.num_slots()

        self.assertEqual(num_slots_1, num_slots_0 + 1)
        self.assertEqual(self.inventory.slot_is_persistent(num_slots_1), persistent)

        inventory_slot_created_events = _fetch_events_chunk(
            web3_client,
            inventory_events.SLOT_CREATED_ABI,
            tx_receipt.block_number,
            tx_receipt.block_number,
        )
        self.assertEqual(len(inventory_slot_created_events), 1)
        self.assertEqual(
            inventory_slot_created_events[0]["args"]["creator"],
            self.admin.address,
        )
        self.assertEqual(
            inventory_slot_created_events[0]["args"]["slot"],
            num_slots_1,
        )

        new_slot_uri_events = _fetch_events_chunk(
            web3_client,
            inventory_events.NEW_SLOT_URI_ABI,
            tx_receipt.block_number,
            tx_receipt.block_number,
        )
        self.assertEqual(len(new_slot_uri_events), 1)
        self.assertEqual(new_slot_uri_events[0]["args"]["slotId"], num_slots_1)

        new_slot_persistence_events = _fetch_events_chunk(
            web3_client,
            inventory_events.NEW_SLOT_PERSISTENCE_ABI,
            tx_receipt.block_number,
            tx_receipt.block_number,
        )
        self.assertEqual(len(new_slot_persistence_events), 1)
        self.assertEqual(new_slot_persistence_events[0]["args"]["slotId"], num_slots_1)
        self.assertEqual(
            new_slot_persistence_events[0]["args"]["persistent"], persistent
        )

    def test_admin_can_set_slot_uri(self):
        persistent = True

        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        num_slots_1 = self.inventory.num_slots()

        # set the slot uri
        tx_receipt = self.inventory.set_slot_uri(
            "some_fancy_slot_uri",
            num_slots_1,
            transaction_config={"from": self.admin},
        )

        new_slot_uri = self.inventory.get_slot_uri(num_slots_1)

        # the slot uri is updated
        self.assertEqual(new_slot_uri, "some_fancy_slot_uri")

        new_slot_uri_events = _fetch_events_chunk(
            web3_client,
            inventory_events.NEW_SLOT_URI_ABI,
            tx_receipt.block_number,
            tx_receipt.block_number,
        )
        self.assertEqual(len(new_slot_uri_events), 1)
        self.assertEqual(new_slot_uri_events[0]["args"]["slotId"], num_slots_1)

    def test_nonadmin_cannot_create_slot(self):
        persistent = True

        num_slots_0 = self.inventory.num_slots()
        with self.assertRaises(VirtualMachineError):
            self.inventory.create_slot(
                persistent,
                slot_uri="random_uri",
                transaction_config={"from": self.player},
            )
        num_slots_1 = self.inventory.num_slots()

        self.assertEqual(num_slots_1, num_slots_0)

    def test_nonadmin_cannot_set_slot_uri(self):
        persistent = True
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        num_slots_0 = self.inventory.num_slots()

        # set the slot uri
        with self.assertRaises(VirtualMachineError):
            self.inventory.set_slot_uri(
                "some_fancy_slot_uri",
                1,
                transaction_config={"from": self.player},
            )

        num_slots_1 = self.inventory.num_slots()

        self.assertEqual(num_slots_1, num_slots_0)

    def test_admin_cannot_mark_contracts_with_invalid_type_as_eligible_for_slots(
        self,
    ):
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        invalid_type = 0

        with self.assertRaises(VirtualMachineError):
            self.inventory.mark_item_as_equippable_in_slot(
                slot,
                invalid_type,
                self.payment_token.address,
                0,
                MAX_UINT,
                {"from": self.admin},
            )

        self.assertEqual(
            self.inventory.max_amount_of_item_in_slot(
                slot, invalid_type, self.payment_token.address, 0
            ),
            0,
        )

    def test_admin_can_mark_erc20_tokens_as_eligible_for_slots(self):
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        erc20_type = 20

        tx_receipt = self.inventory.mark_item_as_equippable_in_slot(
            slot,
            erc20_type,
            self.payment_token.address,
            0,
            MAX_UINT,
            {"from": self.admin},
        )

        self.assertEqual(
            self.inventory.max_amount_of_item_in_slot(
                slot, erc20_type, self.payment_token.address, 0
            ),
            MAX_UINT,
        )

        item_marked_as_equippable_in_slot_events = _fetch_events_chunk(
            web3_client,
            inventory_events.ITEM_MARKED_AS_EQUIPPABLE_IN_SLOT_ABI,
            tx_receipt.block_number,
            tx_receipt.block_number,
        )

        self.assertEqual(len(item_marked_as_equippable_in_slot_events), 1)
        self.assertEqual(
            item_marked_as_equippable_in_slot_events[0]["args"]["slot"],
            slot,
        )
        self.assertEqual(
            item_marked_as_equippable_in_slot_events[0]["args"]["itemType"],
            erc20_type,
        )
        self.assertEqual(
            item_marked_as_equippable_in_slot_events[0]["args"]["itemAddress"],
            self.payment_token.address,
        )
        self.assertEqual(
            item_marked_as_equippable_in_slot_events[0]["args"]["itemPoolId"],
            0,
        )
        self.assertEqual(
            item_marked_as_equippable_in_slot_events[0]["args"]["maxAmount"],
            MAX_UINT,
        )

    def test_nonadmin_cannot_mark_erc20_tokens_as_eligible_for_slots(self):
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        erc20_type = 20

        with self.assertRaises(VirtualMachineError):
            self.inventory.mark_item_as_equippable_in_slot(
                slot,
                erc20_type,
                self.payment_token.address,
                0,
                MAX_UINT,
                {"from": self.player},
            )

        self.assertEqual(
            self.inventory.max_amount_of_item_in_slot(
                slot, erc20_type, self.payment_token.address, 0
            ),
            0,
        )

    def test_admin_cannot_mark_erc20_tokens_as_eligible_for_slots_if_pool_id_is_nonzero(
        self,
    ):
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        erc20_type = 20

        with self.assertRaises(VirtualMachineError):
            self.inventory.mark_item_as_equippable_in_slot(
                slot,
                erc20_type,
                self.payment_token.address,
                1,
                MAX_UINT,
                {"from": self.admin},
            )

        self.assertEqual(
            self.inventory.max_amount_of_item_in_slot(
                slot, erc20_type, self.payment_token.address, 1
            ),
            0,
        )

    def test_admin_can_mark_erc721_tokens_as_eligible_for_slots(self):
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        erc721_type = 721

        tx_receipt = self.inventory.mark_item_as_equippable_in_slot(
            slot,
            erc721_type,
            self.nft.address,
            0,
            1,
            {"from": self.admin},
        )

        self.assertEqual(
            self.inventory.max_amount_of_item_in_slot(
                slot, erc721_type, self.nft.address, 0
            ),
            1,
        )

        item_marked_as_equippable_in_slot_events = _fetch_events_chunk(
            web3_client,
            inventory_events.ITEM_MARKED_AS_EQUIPPABLE_IN_SLOT_ABI,
            tx_receipt.block_number,
            tx_receipt.block_number,
        )

        self.assertEqual(len(item_marked_as_equippable_in_slot_events), 1)
        self.assertEqual(
            item_marked_as_equippable_in_slot_events[0]["args"]["slot"],
            slot,
        )
        self.assertEqual(
            item_marked_as_equippable_in_slot_events[0]["args"]["itemType"],
            erc721_type,
        )
        self.assertEqual(
            item_marked_as_equippable_in_slot_events[0]["args"]["itemAddress"],
            self.nft.address,
        )
        self.assertEqual(
            item_marked_as_equippable_in_slot_events[0]["args"]["itemPoolId"],
            0,
        )
        self.assertEqual(
            item_marked_as_equippable_in_slot_events[0]["args"]["maxAmount"],
            1,
        )

    def test_nonadmin_cannot_mark_erc721_tokens_as_eligible_for_slots(self):
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        erc721_type = 721

        with self.assertRaises(VirtualMachineError):
            self.inventory.mark_item_as_equippable_in_slot(
                slot,
                erc721_type,
                self.nft.address,
                0,
                1,
                {"from": self.player},
            )

        self.assertEqual(
            self.inventory.max_amount_of_item_in_slot(
                slot, erc721_type, self.nft.address, 0
            ),
            0,
        )

    def test_admin_cannot_mark_erc721_tokens_as_eligible_for_slots_if_pool_id_is_nonzero(
        self,
    ):
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        erc721_type = 721

        with self.assertRaises(VirtualMachineError):
            self.inventory.mark_item_as_equippable_in_slot(
                slot,
                erc721_type,
                self.nft.address,
                1,
                1,
                {"from": self.admin},
            )

        self.assertEqual(
            self.inventory.max_amount_of_item_in_slot(
                slot, erc721_type, self.payment_token.address, 1
            ),
            0,
        )

    def test_admin_cannot_mark_erc721_tokens_as_eligible_for_slots_with_max_amount_greater_than_1(
        self,
    ):
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        erc721_type = 721

        with self.assertRaises(VirtualMachineError):
            self.inventory.mark_item_as_equippable_in_slot(
                slot,
                erc721_type,
                self.nft.address,
                0,
                2,
                {"from": self.admin},
            )

        self.assertEqual(
            self.inventory.max_amount_of_item_in_slot(
                slot, erc721_type, self.payment_token.address, 0
            ),
            0,
        )

    def test_admin_can_mark_erc721_tokens_as_eligible_for_slots_with_max_amount_1_then_0(
        self,
    ):
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        erc721_type = 721

        tx_receipt_0 = self.inventory.mark_item_as_equippable_in_slot(
            slot,
            erc721_type,
            self.nft.address,
            0,
            1,
            {"from": self.admin},
        )

        self.assertEqual(
            self.inventory.max_amount_of_item_in_slot(
                slot, erc721_type, self.nft.address, 0
            ),
            1,
        )

        tx_receipt_1 = self.inventory.mark_item_as_equippable_in_slot(
            slot,
            erc721_type,
            self.nft.address,
            0,
            0,
            {"from": self.admin},
        )

        self.assertEqual(
            self.inventory.max_amount_of_item_in_slot(
                slot, erc721_type, self.nft.address, 0
            ),
            0,
        )

        item_marked_as_equippable_in_slot_events = _fetch_events_chunk(
            web3_client,
            inventory_events.ITEM_MARKED_AS_EQUIPPABLE_IN_SLOT_ABI,
            tx_receipt_0.block_number,
            tx_receipt_1.block_number,
        )

        self.assertEqual(len(item_marked_as_equippable_in_slot_events), 2)
        for i, event in enumerate(item_marked_as_equippable_in_slot_events):
            self.assertEqual(
                event["args"]["slot"],
                slot,
            )
            self.assertEqual(
                event["args"]["itemType"],
                erc721_type,
            )
            self.assertEqual(
                event["args"]["itemAddress"],
                self.nft.address,
            )
            self.assertEqual(
                event["args"]["itemPoolId"],
                0,
            )
            self.assertEqual(
                event["args"]["maxAmount"],
                1 - i,
            )

    def test_admin_can_mark_erc1155_tokens_as_eligible_for_slots(self):
        # Testing with non-persistent slot.
        persistent = True
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        erc1155_type = 1155
        item_pool_id = 42
        max_amount = 1337

        tx_receipt = self.inventory.mark_item_as_equippable_in_slot(
            slot,
            erc1155_type,
            self.terminus.address,
            item_pool_id,
            max_amount,
            {"from": self.admin},
        )

        self.assertEqual(
            self.inventory.max_amount_of_item_in_slot(
                slot, erc1155_type, self.terminus.address, item_pool_id
            ),
            max_amount,
        )

        item_marked_as_equippable_in_slot_events = _fetch_events_chunk(
            web3_client,
            inventory_events.ITEM_MARKED_AS_EQUIPPABLE_IN_SLOT_ABI,
            tx_receipt.block_number,
            tx_receipt.block_number,
        )

        self.assertEqual(len(item_marked_as_equippable_in_slot_events), 1)
        self.assertEqual(
            item_marked_as_equippable_in_slot_events[0]["args"]["slot"],
            slot,
        )
        self.assertEqual(
            item_marked_as_equippable_in_slot_events[0]["args"]["itemType"],
            erc1155_type,
        )
        self.assertEqual(
            item_marked_as_equippable_in_slot_events[0]["args"]["itemAddress"],
            self.terminus.address,
        )
        self.assertEqual(
            item_marked_as_equippable_in_slot_events[0]["args"]["itemPoolId"],
            item_pool_id,
        )
        self.assertEqual(
            item_marked_as_equippable_in_slot_events[0]["args"]["maxAmount"],
            max_amount,
        )

    def test_nonadmin_cannot_mark_erc1155_tokens_as_eligible_for_slots(self):
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        erc1155_type = 1155
        item_pool_id = 42
        max_amount = 1337

        with self.assertRaises(VirtualMachineError):
            self.inventory.mark_item_as_equippable_in_slot(
                slot,
                erc1155_type,
                self.terminus.address,
                item_pool_id,
                max_amount,
                {"from": self.player},
            )

        self.assertEqual(
            self.inventory.max_amount_of_item_in_slot(
                slot, erc1155_type, self.terminus.address, item_pool_id
            ),
            0,
        )

    def test_admin_can_set_slot_persistent(self):
        """
        Checks that an admin user can change the persistence of a slot after it has been created.
        """
        # Create slot
        persistent = True
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        self.assertTrue(self.inventory.slot_is_persistent(slot))

        tx_receipt_0 = self.inventory.set_slot_persistent(
            slot,
            False,
            transaction_config={"from": self.admin},
        )

        self.assertFalse(self.inventory.slot_is_persistent(slot))

        new_slot_persistence_events = _fetch_events_chunk(
            web3_client,
            inventory_events.NEW_SLOT_PERSISTENCE_ABI,
            tx_receipt_0.block_number,
            tx_receipt_0.block_number,
        )
        self.assertEqual(len(new_slot_persistence_events), 1)
        self.assertEqual(new_slot_persistence_events[0]["args"]["slotId"], slot)
        self.assertEqual(new_slot_persistence_events[0]["args"]["persistent"], False)

        tx_receipt_1 = self.inventory.set_slot_persistent(
            slot,
            True,
            transaction_config={"from": self.admin},
        )

        self.assertTrue(self.inventory.slot_is_persistent(slot))

        new_slot_persistence_events = _fetch_events_chunk(
            web3_client,
            inventory_events.NEW_SLOT_PERSISTENCE_ABI,
            tx_receipt_1.block_number,
            tx_receipt_1.block_number,
        )
        self.assertEqual(len(new_slot_persistence_events), 1)
        self.assertEqual(new_slot_persistence_events[0]["args"]["slotId"], slot)
        self.assertEqual(new_slot_persistence_events[0]["args"]["persistent"], True)

    def test_nonadmin_cannot_make_persistent_slot_impersistent(self):
        """
        Checks that a non-admin user cannot set the persistence of a slot from persistent to impersistent
        (i.e. from True to False).
        """
        persistent = True
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        self.assertTrue(self.inventory.slot_is_persistent(slot))

        with self.assertRaises(VirtualMachineError):
            self.inventory.set_slot_persistent(
                slot,
                False,
                transaction_config={"from": self.player},
            )

        self.assertTrue(self.inventory.slot_is_persistent(slot))

    def test_nonadmin_cannot_make_impersistent_slot_persistent(self):
        """
        Checks that a non-admin user cannot set the persistence of a slot from impersistent to persistent
        (i.e. from False to True).
        """
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        self.assertFalse(self.inventory.slot_is_persistent(slot))

        with self.assertRaises(VirtualMachineError):
            self.inventory.set_slot_persistent(
                slot,
                True,
                transaction_config={"from": self.player},
            )

        self.assertFalse(self.inventory.slot_is_persistent(slot))


class TestPlayerFlow(InventoryTestCase):
    def test_player_can_equip_erc20_items_onto_their_subject_tokens(self):
        # Mint tokens to player and set approvals
        subject_token_id = self.nft.total_supply()
        self.nft.mint(self.player.address, subject_token_id, {"from": self.owner})
        self.payment_token.mint(self.player.address, 1000, {"from": self.owner})
        self.payment_token.approve(
            self.inventory.address, MAX_UINT, {"from": self.player}
        )

        # Create inventory slot
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        # Set ERC20 token as equippable in slot with max amount of 10
        self.inventory.mark_item_as_equippable_in_slot(
            slot, 20, self.payment_token.address, 0, 10, {"from": self.admin}
        )

        player_balance_0 = self.payment_token.balance_of(self.player.address)
        inventory_balance_0 = self.payment_token.balance_of(self.inventory.address)

        tx_receipt = self.inventory.equip(
            subject_token_id,
            slot,
            20,
            self.payment_token.address,
            0,
            2,
            {"from": self.player},
        )

        player_balance_1 = self.payment_token.balance_of(self.player.address)
        inventory_balance_1 = self.payment_token.balance_of(self.inventory.address)

        self.assertEqual(player_balance_1, player_balance_0 - 2)
        self.assertEqual(inventory_balance_1, inventory_balance_0 + 2)

        equipped_item = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item, (20, self.payment_token.address, 0, 2))

        item_equipped_events = _fetch_events_chunk(
            web3_client,
            inventory_events.ITEM_EQUIPPED_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )
        self.assertEqual(len(item_equipped_events), 1)

        self.assertEqual(
            item_equipped_events[0]["args"]["subjectTokenId"], subject_token_id
        )
        self.assertEqual(item_equipped_events[0]["args"]["slot"], slot)
        self.assertEqual(
            item_equipped_events[0]["args"]["itemType"],
            20,
        )
        self.assertEqual(
            item_equipped_events[0]["args"]["itemAddress"],
            self.payment_token.address,
        )
        self.assertEqual(
            item_equipped_events[0]["args"]["itemTokenId"],
            0,
        )
        self.assertEqual(
            item_equipped_events[0]["args"]["amount"],
            2,
        )
        self.assertEqual(
            item_equipped_events[0]["args"]["equippedBy"],
            self.player.address,
        )

    def test_player_cannot_equip_too_many_erc20_items_onto_their_subject_tokens(self):
        # Mint tokens to player and set approvals
        subject_token_id = self.nft.total_supply()
        self.nft.mint(self.player.address, subject_token_id, {"from": self.owner})
        self.payment_token.mint(self.player.address, 1000, {"from": self.owner})
        self.payment_token.approve(
            self.inventory.address, MAX_UINT, {"from": self.player}
        )

        # Create inventory slot
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        # Set ERC20 token as equippable in slot with max amount of 10
        self.inventory.mark_item_as_equippable_in_slot(
            slot, 20, self.payment_token.address, 0, 10, {"from": self.admin}
        )

        player_balance_0 = self.payment_token.balance_of(self.player.address)
        inventory_balance_0 = self.payment_token.balance_of(self.inventory.address)

        with self.assertRaises(VirtualMachineError):
            self.inventory.equip(
                subject_token_id,
                slot,
                20,
                self.payment_token.address,
                0,
                20,
                {"from": self.player},
            )

        player_balance_1 = self.payment_token.balance_of(self.player.address)
        inventory_balance_1 = self.payment_token.balance_of(self.inventory.address)

        self.assertEqual(player_balance_1, player_balance_0)
        self.assertEqual(inventory_balance_1, inventory_balance_0)

        equipped_item = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item, (0, ZERO_ADDRESS, 0, 0))

    def test_player_can_equip_erc721_items_onto_their_subject_tokens(self):
        # Mint tokens to player and set approvals
        subject_token_id = self.nft.total_supply()
        self.nft.mint(self.player.address, subject_token_id, {"from": self.owner})

        item_token_id = self.item_nft.total_supply()
        self.item_nft.mint(self.player.address, item_token_id, {"from": self.owner})
        self.item_nft.set_approval_for_all(
            self.inventory.address, True, {"from": self.player}
        )

        # Create inventory slot
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        # Set ERC721 token as equippable in slot with max amount of 1
        self.inventory.mark_item_as_equippable_in_slot(
            slot, 721, self.item_nft.address, 0, 1, {"from": self.admin}
        )

        self.assertEqual(self.item_nft.owner_of(item_token_id), self.player.address)

        tx_receipt = self.inventory.equip(
            subject_token_id,
            slot,
            721,
            self.item_nft.address,
            item_token_id,
            1,
            {"from": self.player},
        )

        self.assertEqual(self.item_nft.owner_of(item_token_id), self.inventory.address)

        equipped_item = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item, (721, self.item_nft.address, item_token_id, 1))

        item_equipped_events = _fetch_events_chunk(
            web3_client,
            inventory_events.ITEM_EQUIPPED_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )
        self.assertEqual(len(item_equipped_events), 1)

        self.assertEqual(
            item_equipped_events[0]["args"]["subjectTokenId"], subject_token_id
        )
        self.assertEqual(item_equipped_events[0]["args"]["slot"], slot)
        self.assertEqual(
            item_equipped_events[0]["args"]["itemType"],
            721,
        )
        self.assertEqual(
            item_equipped_events[0]["args"]["itemAddress"],
            self.item_nft.address,
        )
        self.assertEqual(
            item_equipped_events[0]["args"]["itemTokenId"],
            item_token_id,
        )
        self.assertEqual(
            item_equipped_events[0]["args"]["amount"],
            1,
        )
        self.assertEqual(
            item_equipped_events[0]["args"]["equippedBy"],
            self.player.address,
        )

    def test_player_cannot_equip_erc721_items_they_own_onto_subject_tokens_they_do_not_own(
        self,
    ):
        # Mint tokens to player and set approvals
        subject_token_id = self.nft.total_supply()
        self.nft.mint(
            self.random_person.address, subject_token_id, {"from": self.owner}
        )

        item_token_id = self.item_nft.total_supply()
        self.item_nft.mint(self.player.address, item_token_id, {"from": self.owner})
        self.item_nft.set_approval_for_all(
            self.inventory.address, True, {"from": self.player}
        )

        # Create inventory slot
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        # Set ERC721 token as equippable in slot with max amount of 1
        self.inventory.mark_item_as_equippable_in_slot(
            slot, 721, self.item_nft.address, 0, 1, {"from": self.admin}
        )

        self.assertEqual(self.item_nft.owner_of(item_token_id), self.player.address)

        with self.assertRaises(VirtualMachineError):
            self.inventory.equip(
                subject_token_id,
                slot,
                721,
                self.item_nft.address,
                item_token_id,
                1,
                {"from": self.player},
            )

        self.assertEqual(self.item_nft.owner_of(item_token_id), self.player.address)

        equipped_item = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item, (0, ZERO_ADDRESS, 0, 0))

    def test_player_cannot_equip_erc721_items_which_they_do_not_own(self):
        # Mint tokens to player and set approvals
        subject_token_id = self.nft.total_supply()
        self.nft.mint(self.player.address, subject_token_id, {"from": self.owner})

        item_token_id = self.item_nft.total_supply()
        self.item_nft.mint(
            self.random_person.address, item_token_id, {"from": self.owner}
        )
        self.item_nft.set_approval_for_all(
            self.inventory.address, True, {"from": self.random_person}
        )

        # Create inventory slot
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        # Set ERC721 token as equippable in slot with max amount of 1
        self.inventory.mark_item_as_equippable_in_slot(
            slot, 721, self.item_nft.address, 0, 1, {"from": self.admin}
        )

        self.assertEqual(
            self.item_nft.owner_of(item_token_id), self.random_person.address
        )

        with self.assertRaises(VirtualMachineError):
            self.inventory.equip(
                subject_token_id,
                slot,
                721,
                self.item_nft.address,
                item_token_id,
                1,
                {"from": self.player},
            )

        self.assertEqual(
            self.item_nft.owner_of(item_token_id), self.random_person.address
        )

        equipped_item = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item, (0, ZERO_ADDRESS, 0, 0))

    def test_player_can_equip_erc1155_items_onto_their_subject_tokens(self):
        # Mint tokens to player and set approvals
        subject_token_id = self.nft.total_supply()
        self.nft.mint(self.player.address, subject_token_id, {"from": self.owner})

        self.terminus.create_pool_v1(MAX_UINT, True, True, self.owner_tx_config)
        item_pool_id = self.terminus.total_pools()
        self.terminus.mint(
            self.player.address, item_pool_id, 100, "", self.owner_tx_config
        )
        self.terminus.set_approval_for_all(
            self.inventory.address, True, {"from": self.player}
        )

        # Create inventory slot
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        # Set ERC1155 token as equippable in slot with max amount of 10
        self.inventory.mark_item_as_equippable_in_slot(
            slot, 1155, self.terminus.address, item_pool_id, 10, {"from": self.admin}
        )

        player_balance_0 = self.terminus.balance_of(self.player.address, item_pool_id)
        inventory_balance_0 = self.terminus.balance_of(
            self.inventory.address, item_pool_id
        )

        tx_receipt = self.inventory.equip(
            subject_token_id,
            slot,
            1155,
            self.terminus.address,
            item_pool_id,
            10,
            {"from": self.player},
        )

        player_balance_1 = self.terminus.balance_of(self.player.address, item_pool_id)
        inventory_balance_1 = self.terminus.balance_of(
            self.inventory.address, item_pool_id
        )

        self.assertEqual(player_balance_1, player_balance_0 - 10)
        self.assertEqual(inventory_balance_1, inventory_balance_0 + 10)

        equipped_item = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item, (1155, self.terminus.address, item_pool_id, 10))

        item_equipped_events = _fetch_events_chunk(
            web3_client,
            inventory_events.ITEM_EQUIPPED_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )
        self.assertEqual(len(item_equipped_events), 1)

        self.assertEqual(
            item_equipped_events[0]["args"]["subjectTokenId"], subject_token_id
        )
        self.assertEqual(item_equipped_events[0]["args"]["slot"], slot)
        self.assertEqual(
            item_equipped_events[0]["args"]["itemType"],
            1155,
        )
        self.assertEqual(
            item_equipped_events[0]["args"]["itemAddress"],
            self.terminus.address,
        )
        self.assertEqual(
            item_equipped_events[0]["args"]["itemTokenId"],
            item_pool_id,
        )
        self.assertEqual(
            item_equipped_events[0]["args"]["amount"],
            10,
        )
        self.assertEqual(
            item_equipped_events[0]["args"]["equippedBy"],
            self.player.address,
        )

    def test_player_cannot_equip_too_many_erc1155_items_onto_their_subject_tokens(self):
        # Mint tokens to player and set approvals
        subject_token_id = self.nft.total_supply()
        self.nft.mint(self.player.address, subject_token_id, {"from": self.owner})

        self.terminus.create_pool_v1(MAX_UINT, True, True, self.owner_tx_config)
        item_pool_id = self.terminus.total_pools()
        self.terminus.mint(
            self.player.address, item_pool_id, 100, "", self.owner_tx_config
        )
        self.terminus.set_approval_for_all(
            self.inventory.address, True, {"from": self.player}
        )

        # Create inventory slot
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        # Set ERC1155 token as equippable in slot with max amount of 10
        self.inventory.mark_item_as_equippable_in_slot(
            slot, 1155, self.terminus.address, item_pool_id, 10, {"from": self.admin}
        )

        player_balance_0 = self.terminus.balance_of(self.player.address, item_pool_id)
        inventory_balance_0 = self.terminus.balance_of(
            self.inventory.address, item_pool_id
        )

        with self.assertRaises(VirtualMachineError):
            self.inventory.equip(
                subject_token_id,
                slot,
                1155,
                self.terminus.address,
                item_pool_id,
                11,
                {"from": self.player},
            )

        player_balance_1 = self.terminus.balance_of(self.player.address, item_pool_id)
        inventory_balance_1 = self.terminus.balance_of(
            self.inventory.address, item_pool_id
        )

        self.assertEqual(player_balance_1, player_balance_0)
        self.assertEqual(inventory_balance_1, inventory_balance_0)

        equipped_item = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item, (0, ZERO_ADDRESS, 0, 0))

    def test_player_can_unequip_all_erc20_items_in_slot_on_their_subject_tokens(self):
        # Mint tokens to player and set approvals
        subject_token_id = self.nft.total_supply()
        self.nft.mint(self.player.address, subject_token_id, {"from": self.owner})
        self.payment_token.mint(self.player.address, 1000, {"from": self.owner})
        self.payment_token.approve(
            self.inventory.address, MAX_UINT, {"from": self.player}
        )

        # Create inventory slot
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()
        self.assertFalse(self.inventory.slot_is_persistent(slot))

        # Set ERC20 token as equippable in slot with max amount of 10
        self.inventory.mark_item_as_equippable_in_slot(
            slot, 20, self.payment_token.address, 0, 10, {"from": self.admin}
        )

        player_balance_0 = self.payment_token.balance_of(self.player.address)
        inventory_balance_0 = self.payment_token.balance_of(self.inventory.address)

        equipped_item_0 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item_0, (0, ZERO_ADDRESS, 0, 0))

        self.inventory.equip(
            subject_token_id,
            slot,
            20,
            self.payment_token.address,
            0,
            2,
            {"from": self.player},
        )

        player_balance_1 = self.payment_token.balance_of(self.player.address)
        inventory_balance_1 = self.payment_token.balance_of(self.inventory.address)

        self.assertEqual(player_balance_1, player_balance_0 - 2)
        self.assertEqual(inventory_balance_1, inventory_balance_0 + 2)

        equipped_item_1 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item_1, (20, self.payment_token.address, 0, 2))

        tx_receipt = self.inventory.unequip(
            subject_token_id, slot, True, 0, {"from": self.player}
        )

        player_balance_2 = self.payment_token.balance_of(self.player.address)
        inventory_balance_2 = self.payment_token.balance_of(self.inventory.address)

        self.assertEqual(player_balance_2, player_balance_0)
        self.assertEqual(inventory_balance_2, inventory_balance_0)

        equipped_item_2 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item_2, (0, ZERO_ADDRESS, 0, 0))

        item_unequipped_events = _fetch_events_chunk(
            web3_client,
            inventory_events.ITEM_UNEQUIPPED_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )
        self.assertEqual(len(item_unequipped_events), 1)

        self.assertEqual(
            item_unequipped_events[0]["args"]["subjectTokenId"], subject_token_id
        )
        self.assertEqual(item_unequipped_events[0]["args"]["slot"], slot)
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemType"],
            20,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemAddress"],
            self.payment_token.address,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemTokenId"],
            0,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["amount"],
            2,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["unequippedBy"],
            self.player.address,
        )

    def test_player_can_unequip_some_but_not_all_erc20_items_in_slot_on_their_subject_tokens(
        self,
    ):
        # Mint tokens to player and set approvals
        subject_token_id = self.nft.total_supply()
        self.nft.mint(self.player.address, subject_token_id, {"from": self.owner})
        self.payment_token.mint(self.player.address, 1000, {"from": self.owner})
        self.payment_token.approve(
            self.inventory.address, MAX_UINT, {"from": self.player}
        )

        # Create inventory slot
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()
        self.assertFalse(self.inventory.slot_is_persistent(slot))

        # Set ERC20 token as equippable in slot with max amount of 10
        self.inventory.mark_item_as_equippable_in_slot(
            slot, 20, self.payment_token.address, 0, 10, {"from": self.admin}
        )

        player_balance_0 = self.payment_token.balance_of(self.player.address)
        inventory_balance_0 = self.payment_token.balance_of(self.inventory.address)

        equipped_item_0 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item_0, (0, ZERO_ADDRESS, 0, 0))

        self.inventory.equip(
            subject_token_id,
            slot,
            20,
            self.payment_token.address,
            0,
            2,
            {"from": self.player},
        )

        player_balance_1 = self.payment_token.balance_of(self.player.address)
        inventory_balance_1 = self.payment_token.balance_of(self.inventory.address)

        self.assertEqual(player_balance_1, player_balance_0 - 2)
        self.assertEqual(inventory_balance_1, inventory_balance_0 + 2)

        equipped_item_1 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item_1, (20, self.payment_token.address, 0, 2))

        tx_receipt = self.inventory.unequip(
            subject_token_id, slot, False, 1, {"from": self.player}
        )

        player_balance_2 = self.payment_token.balance_of(self.player.address)
        inventory_balance_2 = self.payment_token.balance_of(self.inventory.address)

        self.assertEqual(player_balance_2, player_balance_1 + 1)
        self.assertEqual(inventory_balance_2, inventory_balance_1 - 1)

        equipped_item_2 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item_2, (20, self.payment_token.address, 0, 1))

        item_unequipped_events = _fetch_events_chunk(
            web3_client,
            inventory_events.ITEM_UNEQUIPPED_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )
        self.assertEqual(len(item_unequipped_events), 1)

        self.assertEqual(
            item_unequipped_events[0]["args"]["subjectTokenId"], subject_token_id
        )
        self.assertEqual(item_unequipped_events[0]["args"]["slot"], slot)
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemType"],
            20,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemAddress"],
            self.payment_token.address,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemTokenId"],
            0,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["amount"],
            1,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["unequippedBy"],
            self.player.address,
        )

    def test_player_can_unequip_all_erc721_items_in_slot_on_their_subject_tokens(self):
        # Mint tokens to player and set approvals
        subject_token_id = self.nft.total_supply()
        self.nft.mint(self.player.address, subject_token_id, {"from": self.owner})

        item_token_id = self.item_nft.total_supply()
        self.item_nft.mint(self.player.address, item_token_id, {"from": self.owner})
        self.item_nft.set_approval_for_all(
            self.inventory.address, True, {"from": self.player}
        )

        # Create inventory slot
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()
        self.assertFalse(self.inventory.slot_is_persistent(slot))

        # Set ERC721 token as equippable in slot
        self.inventory.mark_item_as_equippable_in_slot(
            slot, 721, self.item_nft.address, 0, 1, {"from": self.admin}
        )
        self.assertEqual(
            self.inventory.max_amount_of_item_in_slot(
                slot, 721, self.item_nft.address, 0
            ),
            1,
        )

        self.assertEqual(self.item_nft.owner_of(item_token_id), self.player.address)

        equipped_item_0 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item_0, (0, ZERO_ADDRESS, 0, 0))

        self.inventory.equip(
            subject_token_id,
            slot,
            721,
            self.item_nft.address,
            item_token_id,
            1,
            {"from": self.player},
        )

        self.assertEqual(self.item_nft.owner_of(item_token_id), self.inventory.address)

        equipped_item_1 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(
            equipped_item_1, (721, self.item_nft.address, item_token_id, 1)
        )

        tx_receipt = self.inventory.unequip(
            subject_token_id, slot, True, 0, {"from": self.player}
        )

        self.assertEqual(self.item_nft.owner_of(item_token_id), self.player.address)

        equipped_item_2 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item_2, (0, ZERO_ADDRESS, 0, 0))

        item_unequipped_events = _fetch_events_chunk(
            web3_client,
            inventory_events.ITEM_UNEQUIPPED_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )
        self.assertEqual(len(item_unequipped_events), 1)

        self.assertEqual(
            item_unequipped_events[0]["args"]["subjectTokenId"], subject_token_id
        )
        self.assertEqual(item_unequipped_events[0]["args"]["slot"], slot)
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemType"],
            721,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemAddress"],
            self.item_nft.address,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemTokenId"],
            item_token_id,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["amount"],
            1,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["unequippedBy"],
            self.player.address,
        )

    def test_player_can_unequip_single_erc721_item_in_slot_on_their_subject_tokens_by_specifying_amount(
        self,
    ):
        # Mint tokens to player and set approvals
        subject_token_id = self.nft.total_supply()
        self.nft.mint(self.player.address, subject_token_id, {"from": self.owner})

        item_token_id = self.item_nft.total_supply()
        self.item_nft.mint(self.player.address, item_token_id, {"from": self.owner})
        self.item_nft.set_approval_for_all(
            self.inventory.address, True, {"from": self.player}
        )

        # Create inventory slot
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()
        self.assertFalse(self.inventory.slot_is_persistent(slot))

        # Set ERC721 token as equippable in slot
        self.inventory.mark_item_as_equippable_in_slot(
            slot, 721, self.item_nft.address, 0, 1, {"from": self.admin}
        )
        self.assertEqual(
            self.inventory.max_amount_of_item_in_slot(
                slot, 721, self.item_nft.address, 0
            ),
            1,
        )

        self.assertEqual(self.item_nft.owner_of(item_token_id), self.player.address)

        equipped_item_0 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item_0, (0, ZERO_ADDRESS, 0, 0))

        self.inventory.equip(
            subject_token_id,
            slot,
            721,
            self.item_nft.address,
            item_token_id,
            1,
            {"from": self.player},
        )

        self.assertEqual(self.item_nft.owner_of(item_token_id), self.inventory.address)

        equipped_item_1 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(
            equipped_item_1, (721, self.item_nft.address, item_token_id, 1)
        )

        tx_receipt = self.inventory.unequip(
            subject_token_id, slot, False, 1, {"from": self.player}
        )

        self.assertEqual(self.item_nft.owner_of(item_token_id), self.player.address)

        equipped_item_2 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item_2, (0, ZERO_ADDRESS, 0, 0))

        item_unequipped_events = _fetch_events_chunk(
            web3_client,
            inventory_events.ITEM_UNEQUIPPED_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )
        self.assertEqual(len(item_unequipped_events), 1)

        self.assertEqual(
            item_unequipped_events[0]["args"]["subjectTokenId"], subject_token_id
        )
        self.assertEqual(item_unequipped_events[0]["args"]["slot"], slot)
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemType"],
            721,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemAddress"],
            self.item_nft.address,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemTokenId"],
            item_token_id,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["amount"],
            1,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["unequippedBy"],
            self.player.address,
        )

    def test_player_can_unequip_all_erc1155_items_in_slot_on_their_subject_tokens(self):
        # Mint tokens to player and set approvals
        subject_token_id = self.nft.total_supply()
        self.nft.mint(self.player.address, subject_token_id, {"from": self.owner})

        self.terminus.create_pool_v1(MAX_UINT, True, True, self.owner_tx_config)
        item_pool_id = self.terminus.total_pools()
        self.terminus.mint(
            self.player.address, item_pool_id, 100, "", self.owner_tx_config
        )
        self.terminus.set_approval_for_all(
            self.inventory.address, True, {"from": self.player}
        )

        # Create inventory slot
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        # Set ERC1155 token as equippable in slot with max amount of 10
        self.inventory.mark_item_as_equippable_in_slot(
            slot, 1155, self.terminus.address, item_pool_id, 10, {"from": self.admin}
        )

        player_balance_0 = self.terminus.balance_of(self.player.address, item_pool_id)
        inventory_balance_0 = self.terminus.balance_of(
            self.inventory.address, item_pool_id
        )

        equipped_item_0 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item_0, (0, ZERO_ADDRESS, 0, 0))

        self.inventory.equip(
            subject_token_id,
            slot,
            1155,
            self.terminus.address,
            item_pool_id,
            9,
            {"from": self.player},
        )

        player_balance_1 = self.terminus.balance_of(self.player.address, item_pool_id)
        inventory_balance_1 = self.terminus.balance_of(
            self.inventory.address, item_pool_id
        )

        self.assertEqual(player_balance_1, player_balance_0 - 9)
        self.assertEqual(inventory_balance_1, inventory_balance_0 + 9)

        equipped_item_1 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(
            equipped_item_1, (1155, self.terminus.address, item_pool_id, 9)
        )

        tx_receipt = self.inventory.unequip(
            subject_token_id, slot, True, 0, {"from": self.player}
        )

        player_balance_2 = self.terminus.balance_of(self.player.address, item_pool_id)
        inventory_balance_2 = self.terminus.balance_of(
            self.inventory.address, item_pool_id
        )

        self.assertEqual(player_balance_2, player_balance_0)
        self.assertEqual(inventory_balance_2, inventory_balance_0)

        equipped_item_2 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item_2, (0, ZERO_ADDRESS, 0, 0))

        item_unequipped_events = _fetch_events_chunk(
            web3_client,
            inventory_events.ITEM_UNEQUIPPED_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )
        self.assertEqual(len(item_unequipped_events), 1)

        self.assertEqual(
            item_unequipped_events[0]["args"]["subjectTokenId"], subject_token_id
        )
        self.assertEqual(item_unequipped_events[0]["args"]["slot"], slot)
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemType"],
            1155,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemAddress"],
            self.terminus.address,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemTokenId"],
            item_pool_id,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["amount"],
            9,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["unequippedBy"],
            self.player.address,
        )

    def test_player_can_unequip_some_but_not_all_erc1155_items_in_slot_on_their_subject_tokens(
        self,
    ):
        # Mint tokens to player and set approvals
        subject_token_id = self.nft.total_supply()
        self.nft.mint(self.player.address, subject_token_id, {"from": self.owner})

        self.terminus.create_pool_v1(MAX_UINT, True, True, self.owner_tx_config)
        item_pool_id = self.terminus.total_pools()
        self.terminus.mint(
            self.player.address, item_pool_id, 100, "", self.owner_tx_config
        )
        self.terminus.set_approval_for_all(
            self.inventory.address, True, {"from": self.player}
        )

        # Create inventory slot
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        # Set ERC1155 token as equippable in slot with max amount of 10
        self.inventory.mark_item_as_equippable_in_slot(
            slot, 1155, self.terminus.address, item_pool_id, 10, {"from": self.admin}
        )

        player_balance_0 = self.terminus.balance_of(self.player.address, item_pool_id)
        inventory_balance_0 = self.terminus.balance_of(
            self.inventory.address, item_pool_id
        )

        equipped_item_0 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item_0, (0, ZERO_ADDRESS, 0, 0))

        self.inventory.equip(
            subject_token_id,
            slot,
            1155,
            self.terminus.address,
            item_pool_id,
            9,
            {"from": self.player},
        )

        player_balance_1 = self.terminus.balance_of(self.player.address, item_pool_id)
        inventory_balance_1 = self.terminus.balance_of(
            self.inventory.address, item_pool_id
        )

        self.assertEqual(player_balance_1, player_balance_0 - 9)
        self.assertEqual(inventory_balance_1, inventory_balance_0 + 9)

        equipped_item_1 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(
            equipped_item_1, (1155, self.terminus.address, item_pool_id, 9)
        )

        tx_receipt = self.inventory.unequip(
            subject_token_id, slot, False, 5, {"from": self.player}
        )

        player_balance_2 = self.terminus.balance_of(self.player.address, item_pool_id)
        inventory_balance_2 = self.terminus.balance_of(
            self.inventory.address, item_pool_id
        )

        self.assertEqual(player_balance_2, player_balance_1 + 5)
        self.assertEqual(inventory_balance_2, inventory_balance_1 - 5)

        equipped_item_2 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(
            equipped_item_2, (1155, self.terminus.address, item_pool_id, 4)
        )

        item_unequipped_events = _fetch_events_chunk(
            web3_client,
            inventory_events.ITEM_UNEQUIPPED_ABI,
            from_block=tx_receipt.block_number,
            to_block=tx_receipt.block_number,
        )
        self.assertEqual(len(item_unequipped_events), 1)

        self.assertEqual(
            item_unequipped_events[0]["args"]["subjectTokenId"], subject_token_id
        )
        self.assertEqual(item_unequipped_events[0]["args"]["slot"], slot)
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemType"],
            1155,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemAddress"],
            self.terminus.address,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemTokenId"],
            item_pool_id,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["amount"],
            5,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["unequippedBy"],
            self.player.address,
        )

    def test_player_can_equip_an_item_and_then_replace_it_onto_their_subject_tokens_20_then_1155(
        self,
    ):
        # Mint tokens to player and set approvals
        subject_token_id = self.nft.total_supply()
        self.nft.mint(self.player.address, subject_token_id, {"from": self.owner})

        self.payment_token.mint(self.player.address, 1000, {"from": self.owner})
        self.payment_token.approve(
            self.inventory.address, MAX_UINT, {"from": self.player}
        )

        self.terminus.create_pool_v1(MAX_UINT, True, True, self.owner_tx_config)
        item_pool_id = self.terminus.total_pools()
        self.terminus.mint(
            self.player.address, item_pool_id, 100, "", self.owner_tx_config
        )
        self.terminus.set_approval_for_all(
            self.inventory.address, True, {"from": self.player}
        )

        # Create inventory slot
        persistent = False
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()

        # Set ERC20 token as equippable in slot with max amount of 10
        self.inventory.mark_item_as_equippable_in_slot(
            slot, 20, self.payment_token.address, 0, 10, {"from": self.admin}
        )

        # Set ERC1155 token as equippable in slot with max amount of 10
        self.inventory.mark_item_as_equippable_in_slot(
            slot, 1155, self.terminus.address, item_pool_id, 10, {"from": self.admin}
        )

        player_erc20_balance_0 = self.payment_token.balance_of(self.player.address)
        inventory_erc20_balance_0 = self.payment_token.balance_of(
            self.inventory.address
        )

        tx_receipt_0 = self.inventory.equip(
            subject_token_id,
            slot,
            20,
            self.payment_token.address,
            0,
            2,
            {"from": self.player},
        )

        player_erc20_balance_1 = self.payment_token.balance_of(self.player.address)
        inventory_erc20_balance_1 = self.payment_token.balance_of(
            self.inventory.address
        )

        self.assertEqual(player_erc20_balance_1, player_erc20_balance_0 - 2)
        self.assertEqual(inventory_erc20_balance_1, inventory_erc20_balance_0 + 2)

        equipped_item = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item, (20, self.payment_token.address, 0, 2))

        player_erc1155_balance_1 = self.terminus.balance_of(
            self.player.address, item_pool_id
        )
        inventory_erc1155_balance_1 = self.terminus.balance_of(
            self.inventory.address, item_pool_id
        )

        tx_receipt_1 = self.inventory.equip(
            subject_token_id,
            slot,
            1155,
            self.terminus.address,
            item_pool_id,
            9,
            {"from": self.player},
        )

        player_erc20_balance_2 = self.payment_token.balance_of(self.player.address)
        inventory_erc20_balance_2 = self.payment_token.balance_of(
            self.inventory.address
        )

        self.assertEqual(player_erc20_balance_2, player_erc20_balance_0)
        self.assertEqual(inventory_erc20_balance_2, inventory_erc20_balance_0)

        equipped_item = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item, (1155, self.terminus.address, item_pool_id, 9))

        player_erc1155_balance_2 = self.terminus.balance_of(
            self.player.address, item_pool_id
        )
        inventory_erc1155_balance_2 = self.terminus.balance_of(
            self.inventory.address, item_pool_id
        )

        self.assertEqual(player_erc1155_balance_2, player_erc1155_balance_1 - 9)
        self.assertEqual(inventory_erc1155_balance_2, inventory_erc1155_balance_1 + 9)

        item_equipped_events = _fetch_events_chunk(
            web3_client,
            inventory_events.ITEM_EQUIPPED_ABI,
            from_block=tx_receipt_0.block_number,
            to_block=tx_receipt_1.block_number,
        )
        self.assertEqual(len(item_equipped_events), 2)

        self.assertEqual(
            item_equipped_events[0]["args"]["subjectTokenId"], subject_token_id
        )
        self.assertEqual(item_equipped_events[0]["args"]["slot"], slot)
        self.assertEqual(
            item_equipped_events[0]["args"]["itemType"],
            20,
        )
        self.assertEqual(
            item_equipped_events[0]["args"]["itemAddress"],
            self.payment_token.address,
        )
        self.assertEqual(
            item_equipped_events[0]["args"]["itemTokenId"],
            0,
        )
        self.assertEqual(
            item_equipped_events[0]["args"]["amount"],
            2,
        )
        self.assertEqual(
            item_equipped_events[0]["args"]["equippedBy"],
            self.player.address,
        )

        self.assertEqual(
            item_equipped_events[1]["args"]["subjectTokenId"], subject_token_id
        )
        self.assertEqual(item_equipped_events[1]["args"]["slot"], slot)
        self.assertEqual(
            item_equipped_events[1]["args"]["itemType"],
            1155,
        )
        self.assertEqual(
            item_equipped_events[1]["args"]["itemAddress"],
            self.terminus.address,
        )
        self.assertEqual(
            item_equipped_events[1]["args"]["itemTokenId"],
            item_pool_id,
        )
        self.assertEqual(
            item_equipped_events[1]["args"]["amount"],
            9,
        )
        self.assertEqual(
            item_equipped_events[1]["args"]["equippedBy"],
            self.player.address,
        )

        item_unequipped_events = _fetch_events_chunk(
            web3_client,
            inventory_events.ITEM_UNEQUIPPED_ABI,
            from_block=tx_receipt_1.block_number,
            to_block=tx_receipt_1.block_number,
        )
        self.assertEqual(len(item_unequipped_events), 1)
        self.assertEqual(
            item_unequipped_events[0]["args"]["subjectTokenId"], subject_token_id
        )
        self.assertEqual(item_unequipped_events[0]["args"]["slot"], slot)
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemType"],
            20,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemAddress"],
            self.payment_token.address,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["itemTokenId"],
            0,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["amount"],
            2,
        )
        self.assertEqual(
            item_unequipped_events[0]["args"]["unequippedBy"],
            self.player.address,
        )

    def test_player_cannot_unequip_erc20_tokens_from_persistent_slot_but_can_increase_amount(self):
        """
        Checks that, once a player has equipped eligible ERC20 tokens into a persistent slot, they
        cannot be unequipped without a change in persistence.
        """
        # Mint tokens to player and set approvals
        subject_token_id = self.nft.total_supply()
        self.nft.mint(self.player.address, subject_token_id, {"from": self.owner})
        self.payment_token.mint(self.player.address, 1000, {"from": self.owner})
        self.payment_token.approve(
            self.inventory.address, MAX_UINT, {"from": self.player}
        )

        # Create inventory slot
        persistent = True
        self.inventory.create_slot(
            persistent,
            slot_uri="random_uri",
            transaction_config={"from": self.admin},
        )
        slot = self.inventory.num_slots()
        self.assertTrue(self.inventory.slot_is_persistent(slot))

        # Set ERC20 token as equippable in slot with max amount of 10
        self.inventory.mark_item_as_equippable_in_slot(
            slot, 20, self.payment_token.address, 0, 10, {"from": self.admin}
        )

        player_balance_0 = self.payment_token.balance_of(self.player.address)
        inventory_balance_0 = self.payment_token.balance_of(self.inventory.address)

        equipped_item_0 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item_0, (0, ZERO_ADDRESS, 0, 0))

        self.inventory.equip(
            subject_token_id,
            slot,
            20,
            self.payment_token.address,
            0,
            2,
            {"from": self.player},
        )

        player_balance_1 = self.payment_token.balance_of(self.player.address)
        inventory_balance_1 = self.payment_token.balance_of(self.inventory.address)

        self.assertEqual(player_balance_1, player_balance_0 - 2)
        self.assertEqual(inventory_balance_1, inventory_balance_0 + 2)

        equipped_item_1 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item_1, (20, self.payment_token.address, 0, 2))

        with self.assertRaises(VirtualMachineError):
            self.inventory.unequip(
                subject_token_id, slot, False, 1, {"from": self.player}
            )

        player_balance_2 = self.payment_token.balance_of(self.player.address)
        inventory_balance_2 = self.payment_token.balance_of(self.inventory.address)

        self.assertEqual(player_balance_2, player_balance_1)
        self.assertEqual(inventory_balance_2, inventory_balance_1)

        equipped_item_2 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item_2, (20, self.payment_token.address, 0, 2))

        """
        TODO(zomglings): There is currently a bug in the contract which prevents players from increasing
        the amount of ERC20 tokens in a persistent slot (even if the total amount would be below the
        maximum allowable amount for that token in that slot). Once this bug has been fixed, this test
        should be extended with the following code:

        self.inventory.equip(
            subject_token_id,
            slot,
            20,
            self.payment_token.address,
            0,
            3,
            {"from": self.player},
        )

        player_balance_3 = self.payment_token.balance_of(self.player.address)
        inventory_balance_3 = self.payment_token.balance_of(self.inventory.address)

        self.assertEqual(player_balance_3, player_balance_2 - 3)
        self.assertEqual(inventory_balance_3, inventory_balance_2 + 3)

        equipped_item_3 = self.inventory.get_equipped_item(subject_token_id, slot)
        self.assertEqual(equipped_item_3, (20, self.payment_token.address, 0, 5))
        """
