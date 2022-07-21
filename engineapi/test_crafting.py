from typing import List
import unittest

from brownie import accounts, network
from brownie.exceptions import VirtualMachineError
from brownie.network import web3 as web3_client
from eth_typing import ChecksumAddress

from . import Diamond, CraftingFacet, MockErc20, MockERC1155
from .core import diamond_gogogo, facet_cut


class CraftingItem:
    def __init__(
        self,
        token_type: int,
        token_address: ChecksumAddress,
        token_id: int,
        amount: int,
        token_action: int,
    ):
        self.token_type = token_type
        self.token_address = token_address
        self.token_id = token_id
        self.amount = amount
        self.token_action = token_action

    def to_tuple(self):
        return (
            self.token_type,
            self.token_address,
            self.token_id,
            self.amount,
            self.token_action,
        )


class CraftingInput(CraftingItem):
    pass


class CraftingOutput(CraftingItem):
    pass


class Recipe:
    def __init__(
        self,
        inputs: List[CraftingInput],
        outputs: List[CraftingOutput],
        is_active: bool,
    ):
        self.inputs = inputs
        self.outputs = outputs
        self.is_active = is_active

    def to_tuple(self):
        return (
            [i.to_tuple() for i in self.inputs],
            [o.to_tuple() for o in self.outputs],
            self.is_active,
        )


class CraftingTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            network.connect()
        except:
            pass

        cls.erc20_contracts = [MockErc20.MockErc20(None) for _ in range(10)]
        for i, contract in enumerate(cls.erc20_contracts):
            contract.deploy(f"Mock Erc20-{i}", "MOCKERC20-{i}", {"from": accounts[0]})

        cls.erc1155_contracts = [MockERC1155.MockERC1155(None) for _ in range(10)]
        for i, contract in enumerate(cls.erc1155_contracts):
            contract.deploy({"from": accounts[0]})

        gogogo_result = diamond_gogogo(
            accounts[0],
            {"from": accounts[0]},
        )

        cls.diamond_address = gogogo_result["Diamond"]

        crafting_facet = CraftingFacet.CraftingFacet(None)
        crafting_facet.deploy({"from": accounts[0]})
        facet_cut(
            cls.diamond_address,
            "CraftingFacet",
            crafting_facet.address,
            "add",
            {"from": accounts[0]},
        )

        cls.crafting = CraftingFacet.CraftingFacet(cls.diamond_address)

    def _create_recipe(
        self,
        recipe: Recipe,
    ) -> int:
        self.crafting.add_recipe(recipe.to_tuple(), {"from": accounts[0]})
        recipe_id = self.crafting.num_recipes()
        return recipe_id

    def test_create_craft(self):
        inputs = [
            CraftingInput(
                20,
                self.erc20_contracts[1].address,
                0,
                10 * 10 ** 18,
                0,
            ),
        ]
        outputs = [
            CraftingOutput(
                20,
                self.erc20_contracts[2].address,
                0,
                10 * 10 ** 18,
                0,
            ),
        ]
        num_recipes_before = self.crafting.num_recipes()
        recipe = Recipe(inputs, outputs, True)
        recipe_id = self._create_recipe(recipe)
        num_recipes_after = self.crafting.num_recipes()

        self.assertEqual(num_recipes_after, num_recipes_before + 1)

        recipe_from_contract = self.crafting.get_recipe(recipe_id)
        self.assertEqual(recipe_from_contract, recipe.to_tuple())

    def _check_balances_after_crafting(self, recipe: Recipe, block_no_before: int):
        for input in recipe.inputs:
            (
                balance_user_before,
                balance_user_after,
                balance_contract_before,
                balance_contract_after,
            ) = (None, None, None, None)
            if input.token_type == 20:
                erc20_contract = MockErc20.MockErc20(input.token_address)
                balance_user_before = erc20_contract.balance_of(
                    accounts[1], block_number=block_no_before
                )
                balance_user_after = erc20_contract.balance_of(accounts[1])
                balance_contract_before = erc20_contract.balance_of(
                    self.crafting.address, block_number=block_no_before
                )
                balance_contract_after = erc20_contract.balance_of(
                    self.crafting.address
                )
            elif input.token_type == 1155:
                erc1155_contract = MockERC1155.MockERC1155(input.token_address)
                balance_user_before = erc1155_contract.balance_of(
                    accounts[1], input.token_id, block_number=block_no_before
                )
                balance_user_after = erc1155_contract.balance_of(
                    accounts[1], input.token_id
                )
                balance_contract_before = erc1155_contract.balance_of(
                    self.crafting.address, input.token_id, block_number=block_no_before
                )
                balance_contract_after = erc1155_contract.balance_of(
                    self.crafting.address,
                    input.token_id,
                )

            if input.token_action == 0:
                # transfer
                self.assertEqual(balance_user_before - input.amount, balance_user_after)
                self.assertEqual(
                    balance_contract_before + input.amount, balance_contract_after
                )

            elif input.token_action == 1:
                # burn
                self.assertEqual(balance_user_before - input.amount, balance_user_after)
                self.assertEqual(balance_contract_before, balance_contract_after)

            elif input.token_action == 2:
                # hold
                self.assertEqual(balance_user_before, balance_user_after)
                self.assertEqual(balance_contract_before, balance_contract_after)

        for output in recipe.outputs:
            (
                balance_user_before,
                balance_user_after,
                balance_contract_before,
                balance_contract_after,
            ) = (None, None, None, None)
            if output.token_type == 20:
                erc20_contract = MockErc20.MockErc20(output.token_address)
                balance_user_before = erc20_contract.balance_of(
                    accounts[1], block_number=block_no_before
                )
                balance_user_after = erc20_contract.balance_of(accounts[1])
                balance_contract_before = erc20_contract.balance_of(
                    self.crafting.address, block_number=block_no_before
                )
                balance_contract_after = erc20_contract.balance_of(
                    self.crafting.address
                )
            elif output.token_type == 1155:
                erc1155_contract = MockERC1155.MockERC1155(output.token_address)
                balance_user_before = erc1155_contract.balance_of(
                    accounts[1], output.token_id, block_number=block_no_before
                )
                balance_user_after = erc1155_contract.balance_of(
                    accounts[1], output.token_id
                )
                balance_contract_before = erc1155_contract.balance_of(
                    self.crafting.address, output.token_id, block_number=block_no_before
                )
                balance_contract_after = erc1155_contract.balance_of(
                    self.crafting.address, output.token_id
                )

            if output.token_action == 0:
                # transfer
                self.assertEqual(
                    balance_user_before + output.amount, balance_user_after
                )
                self.assertEqual(
                    balance_contract_before - output.amount, balance_contract_after
                )
            elif output.token_action == 1:
                # mint
                self.assertEqual(
                    balance_user_before + output.amount, balance_user_after
                )
                self.assertEqual(balance_contract_before, balance_contract_after)

    def test_simple_transfer_craft(self):
        input_amount = 10 * 10 ** 18
        output_amount = 10 * 10 ** 18
        inputs = [
            CraftingInput(
                20,
                self.erc20_contracts[1].address,
                0,
                input_amount,
                0,
            ),
        ]
        outputs = [
            CraftingOutput(
                20,
                self.erc20_contracts[2].address,
                0,
                output_amount,
                0,
            ),
        ]

        recipe = Recipe(inputs, outputs, True)
        recipe_id = self._create_recipe(recipe)

        self.erc20_contracts[1].mint(accounts[1], input_amount, {"from": accounts[0]})
        self.erc20_contracts[2].mint(
            self.crafting.address, output_amount, {"from": accounts[0]}
        )

        self.erc20_contracts[1].approve(
            self.crafting.address, input_amount, {"from": accounts[1]}
        )
        block_no_before = web3_client.eth.block_number
        self.crafting.craft(recipe_id, {"from": accounts[1]})

        self._check_balances_after_crafting(recipe, block_no_before)

    def test_simple_transfer_craft_with_erc1155(self):
        input_amount = 10 * 10 ** 18
        output_amount = 10 * 10 ** 18

        input_erc1155_amount = 1
        output_erc1155_amount = 1

        inputs = [
            CraftingInput(
                20,
                self.erc20_contracts[1].address,
                0,
                input_amount,
                0,
            ),
            CraftingInput(
                1155,
                self.erc1155_contracts[1].address,
                1,
                input_erc1155_amount,
                0,
            ),
        ]
        outputs = [
            CraftingOutput(
                20,
                self.erc20_contracts[2].address,
                0,
                output_amount,
                0,
            ),
            CraftingOutput(
                1155,
                self.erc1155_contracts[1].address,
                2,
                output_erc1155_amount,
                0,
            ),
        ]

        recipe = Recipe(inputs, outputs, True)
        recipe_id = self._create_recipe(recipe)

        self.erc20_contracts[1].mint(accounts[1], input_amount, {"from": accounts[0]})
        self.erc20_contracts[2].mint(
            self.crafting.address, output_amount, {"from": accounts[0]}
        )

        self.erc1155_contracts[1].mint(
            accounts[1], 1, input_erc1155_amount, b"", {"from": accounts[0]}
        )
        self.erc1155_contracts[1].mint(
            self.crafting.address, 2, output_erc1155_amount, b"", {"from": accounts[0]}
        )

        self.erc20_contracts[1].approve(
            self.crafting.address, input_amount, {"from": accounts[1]}
        )
        self.erc1155_contracts[1].set_approval_for_all(
            self.crafting.address, True, {"from": accounts[1]}
        )

        block_no_before = web3_client.eth.block_number
        self.crafting.craft(recipe_id, {"from": accounts[1]})

        self._check_balances_after_crafting(recipe, block_no_before)

    def test_craft_with_burn_and_mint(self):
        input_amount = 10 * 10 ** 18
        output_amount = 10 * 10 ** 18

        input_erc1155_amount = 1
        output_erc1155_amount = 1

        inputs = [
            CraftingInput(
                20,
                self.erc20_contracts[1].address,
                0,
                input_amount,
                token_action=1,  # burn
            ),
            CraftingInput(
                1155,
                self.erc1155_contracts[1].address,
                1,
                input_erc1155_amount,
                1,  # burn
            ),
        ]
        outputs = [
            CraftingOutput(
                20,
                self.erc20_contracts[2].address,
                0,
                output_amount,
                1,  # mint
            ),
            CraftingOutput(
                1155,
                self.erc1155_contracts[1].address,
                2,
                output_erc1155_amount,
                1,  # mint
            ),
        ]

        recipe = Recipe(inputs, outputs, True)
        recipe_id = self._create_recipe(recipe)

        self.erc20_contracts[1].mint(accounts[1], input_amount, {"from": accounts[0]})
        self.erc20_contracts[2].mint(
            self.crafting.address, output_amount, {"from": accounts[0]}
        )

        self.erc1155_contracts[1].mint(
            accounts[1], 1, input_erc1155_amount, b"", {"from": accounts[0]}
        )
        self.erc1155_contracts[1].mint(
            self.crafting.address, 2, output_erc1155_amount, b"", {"from": accounts[0]}
        )

        self.erc20_contracts[1].approve(
            self.crafting.address, input_amount, {"from": accounts[1]}
        )
        self.erc1155_contracts[1].set_approval_for_all(
            self.crafting.address, True, {"from": accounts[1]}
        )

        block_no_before = web3_client.eth.block_number
        self.crafting.craft(recipe_id, {"from": accounts[1]})
        self._check_balances_after_crafting(recipe, block_no_before)

    def test_craft_with_burn_and_mint(self):
        input_amount = 10 * 10 ** 18
        output_amount = 10 * 10 ** 18

        input_erc1155_amount = 1
        output_erc1155_amount = 1

        inputs = [
            CraftingInput(
                20,
                self.erc20_contracts[1].address,
                0,
                input_amount,
                token_action=1,  # burn
            ),
            CraftingInput(
                1155,
                self.erc1155_contracts[1].address,
                1,
                input_erc1155_amount,
                1,  # burn
            ),
        ]
        outputs = [
            CraftingOutput(
                20,
                self.erc20_contracts[2].address,
                0,
                output_amount,
                1,  # mint
            ),
            CraftingOutput(
                1155,
                self.erc1155_contracts[1].address,
                2,
                output_erc1155_amount,
                1,  # mint
            ),
        ]

        recipe = Recipe(inputs, outputs, True)
        recipe_id = self._create_recipe(recipe)

        self.erc20_contracts[1].mint(accounts[1], input_amount, {"from": accounts[0]})
        self.erc20_contracts[2].mint(
            self.crafting.address, output_amount, {"from": accounts[0]}
        )

        self.erc1155_contracts[1].mint(
            accounts[1], 1, input_erc1155_amount, b"", {"from": accounts[0]}
        )
        self.erc1155_contracts[1].mint(
            self.crafting.address, 2, output_erc1155_amount, b"", {"from": accounts[0]}
        )

        self.erc20_contracts[1].approve(
            self.crafting.address, input_amount, {"from": accounts[1]}
        )
        self.erc1155_contracts[1].set_approval_for_all(
            self.crafting.address, True, {"from": accounts[1]}
        )

        block_no_before = web3_client.eth.block_number
        self.crafting.craft(recipe_id, {"from": accounts[1]})

        self._check_balances_after_crafting(recipe, block_no_before)

    def test_craft_with_hold_and_mint(self):
        input_amount = 10 * 10 ** 18
        output_amount = 10 * 10 ** 18

        input_erc1155_amount = 1
        output_erc1155_amount = 1

        inputs = [
            CraftingInput(
                20,
                self.erc20_contracts[1].address,
                0,
                input_amount,
                token_action=2,  # hold
            ),
            CraftingInput(
                1155,
                self.erc1155_contracts[1].address,
                1,
                input_erc1155_amount,
                2,  # hold
            ),
        ]
        outputs = [
            CraftingOutput(
                20,
                self.erc20_contracts[2].address,
                0,
                output_amount,
                1,  # mint
            ),
            CraftingOutput(
                1155,
                self.erc1155_contracts[1].address,
                2,
                output_erc1155_amount,
                1,  # mint
            ),
        ]

        recipe = Recipe(inputs, outputs, True)
        recipe_id = self._create_recipe(recipe)

        self.erc20_contracts[1].mint(accounts[1], input_amount, {"from": accounts[0]})
        self.erc20_contracts[2].mint(
            self.crafting.address, output_amount, {"from": accounts[0]}
        )

        self.erc1155_contracts[1].mint(
            accounts[1], 1, input_erc1155_amount, b"", {"from": accounts[0]}
        )
        self.erc1155_contracts[1].mint(
            self.crafting.address, 2, output_erc1155_amount, b"", {"from": accounts[0]}
        )

        self.erc20_contracts[1].approve(
            self.crafting.address, input_amount, {"from": accounts[1]}
        )
        self.erc1155_contracts[1].set_approval_for_all(
            self.crafting.address, True, {"from": accounts[1]}
        )

        block_no_before = web3_client.eth.block_number
        self.crafting.craft(recipe_id, {"from": accounts[1]})

        self._check_balances_after_crafting(recipe, block_no_before)

    def test_craft_with_all_type_of_operations(self):
        input_amount = 10 * 10 ** 18
        output_amount = 10 * 10 ** 18

        input_erc1155_amount = 1
        output_erc1155_amount = 1

        inputs = [
            CraftingInput(
                20,
                self.erc20_contracts[1].address,
                0,
                input_amount,
                token_action=2,  # hold
            ),
            CraftingInput(
                1155,
                self.erc1155_contracts[1].address,
                1,
                input_erc1155_amount,
                2,  # hold
            ),
            CraftingInput(
                20,
                self.erc20_contracts[2].address,
                0,
                input_amount,
                token_action=1,  # burn
            ),
            CraftingInput(
                1155,
                self.erc1155_contracts[1].address,
                10,
                input_erc1155_amount,
                1,  # burn
            ),
            CraftingInput(
                20,
                self.erc20_contracts[3].address,
                0,
                input_amount,
                token_action=0,  # transfer
            ),
            CraftingInput(
                1155,
                self.erc1155_contracts[1].address,
                20,
                input_erc1155_amount,
                0,  # transfer
            ),
        ]
        outputs = [
            CraftingOutput(
                20,
                self.erc20_contracts[4].address,
                0,
                output_amount,
                1,  # mint
            ),
            CraftingOutput(
                1155,
                self.erc1155_contracts[1].address,
                2,
                output_erc1155_amount,
                1,  # mint
            ),
            CraftingOutput(
                20,
                self.erc20_contracts[5].address,
                0,
                output_amount,
                0,  # transfer
            ),
            CraftingOutput(
                1155,
                self.erc1155_contracts[1].address,
                11,
                output_erc1155_amount,
                0,  # transfer
            ),
        ]

        recipe = Recipe(inputs, outputs, True)
        recipe_id = self._create_recipe(recipe)

        for input in inputs:
            if input.token_type == 20:
                contract = MockErc20.MockErc20(input.token_address)
                contract.mint(accounts[1], input.amount, {"from": accounts[0]})
                contract.increase_allowance(
                    self.crafting.address, input.amount, {"from": accounts[1]}
                )
            elif input.token_type == 1155:
                contract = MockERC1155.MockERC1155(input.token_address)
                contract.mint(
                    accounts[1],
                    input.token_id,
                    input.amount,
                    b"",
                    {"from": accounts[0]},
                )
                contract.set_approval_for_all(
                    self.crafting.address, True, {"from": accounts[1]}
                )

        for output in outputs:
            if output.token_action == 0:
                if output.token_type == 20:
                    contract = MockErc20.MockErc20(output.token_address)
                    contract.mint(
                        self.crafting.address, output.amount, {"from": accounts[1]}
                    )
                elif output.token_type == 1155:
                    contract = MockERC1155.MockERC1155(output.token_address)
                    contract.mint(
                        self.crafting.address,
                        output.token_id,
                        output.amount,
                        b"",
                        {"from": accounts[1]},
                    )

        block_no_before = web3_client.eth.block_number
        self.crafting.craft(recipe_id, {"from": accounts[1]})
        self._check_balances_after_crafting(recipe, block_no_before)

    def test_craft_fails_with_unsefficient_amount_hold_only(self):
        input_amount = 10 * 10 ** 18
        output_amount = 10 * 10 ** 18

        input_erc1155_amount = 1
        output_erc1155_amount = 1

        inputs = [
            CraftingInput(
                20,
                self.erc20_contracts[1].address,
                0,
                input_amount,
                token_action=2,  # hold
            ),
            CraftingInput(
                1155,
                self.erc1155_contracts[1].address,
                1,
                input_erc1155_amount,
                2,  # hold
            ),
        ]
        outputs = [
            CraftingOutput(
                20,
                self.erc20_contracts[4].address,
                0,
                output_amount,
                1,  # mint
            ),
            CraftingOutput(
                1155,
                self.erc1155_contracts[1].address,
                2,
                output_erc1155_amount,
                1,  # mint
            ),
            CraftingOutput(
                20,
                self.erc20_contracts[5].address,
                0,
                output_amount,
                0,  # transfer
            ),
            CraftingOutput(
                1155,
                self.erc1155_contracts[1].address,
                11,
                output_erc1155_amount,
                0,  # transfer
            ),
        ]

        recipe = Recipe(inputs, outputs, True)
        recipe_id = self._create_recipe(recipe)

        for output in outputs:
            if output.token_action == 0:
                if output.token_type == 20:
                    contract = MockErc20.MockErc20(output.token_address)
                    contract.mint(
                        self.crafting.address, output.amount, {"from": accounts[1]}
                    )
                elif output.token_type == 1155:
                    contract = MockERC1155.MockERC1155(output.token_address)
                    contract.mint(
                        self.crafting.address,
                        output.token_id,
                        output.amount,
                        b"",
                        {"from": accounts[1]},
                    )

        block_no_before = web3_client.eth.block_number

        with self.assertRaises(VirtualMachineError):
            self.crafting.craft(recipe_id, {"from": accounts[1]})

    def test_craft_fails_with_unsefficient_amount_mint_only(self):
        input_amount = 10 * 10 ** 18
        output_amount = 10 * 10 ** 18

        input_erc1155_amount = 1
        output_erc1155_amount = 1

        inputs = [
            CraftingInput(
                20,
                self.erc20_contracts[1].address,
                0,
                input_amount,
                token_action=1,  # mint
            ),
            CraftingInput(
                1155,
                self.erc1155_contracts[1].address,
                1,
                input_erc1155_amount,
                1,  # mint
            ),
        ]
        outputs = [
            CraftingOutput(
                20,
                self.erc20_contracts[4].address,
                0,
                output_amount,
                1,  # mint
            ),
            CraftingOutput(
                1155,
                self.erc1155_contracts[1].address,
                2,
                output_erc1155_amount,
                1,  # mint
            ),
            CraftingOutput(
                20,
                self.erc20_contracts[5].address,
                0,
                output_amount,
                0,  # transfer
            ),
            CraftingOutput(
                1155,
                self.erc1155_contracts[1].address,
                11,
                output_erc1155_amount,
                0,  # transfer
            ),
        ]

        recipe = Recipe(inputs, outputs, True)
        recipe_id = self._create_recipe(recipe)

        for output in outputs:
            if output.token_action == 0:
                if output.token_type == 20:
                    contract = MockErc20.MockErc20(output.token_address)
                    contract.mint(
                        self.crafting.address, output.amount, {"from": accounts[1]}
                    )
                elif output.token_type == 1155:
                    contract = MockERC1155.MockERC1155(output.token_address)
                    contract.mint(
                        self.crafting.address,
                        output.token_id,
                        output.amount,
                        b"",
                        {"from": accounts[1]},
                    )

        block_no_before = web3_client.eth.block_number

        with self.assertRaises(VirtualMachineError):
            self.crafting.craft(recipe_id, {"from": accounts[1]})

    def test_craft_fails_with_unsefficient_amount_transfer_only(self):
        input_amount = 10 * 10 ** 18
        output_amount = 10 * 10 ** 18

        input_erc1155_amount = 1
        output_erc1155_amount = 1

        inputs = [
            CraftingInput(
                20,
                self.erc20_contracts[1].address,
                0,
                input_amount,
                token_action=0,  # transfer
            ),
            CraftingInput(
                1155,
                self.erc1155_contracts[1].address,
                1,
                input_erc1155_amount,
                0,  # transfer
            ),
        ]
        outputs = [
            CraftingOutput(
                20,
                self.erc20_contracts[4].address,
                0,
                output_amount,
                1,  # mint
            ),
            CraftingOutput(
                1155,
                self.erc1155_contracts[1].address,
                2,
                output_erc1155_amount,
                1,  # mint
            ),
            CraftingOutput(
                20,
                self.erc20_contracts[5].address,
                0,
                output_amount,
                0,  # transfer
            ),
            CraftingOutput(
                1155,
                self.erc1155_contracts[1].address,
                11,
                output_erc1155_amount,
                0,  # transfer
            ),
        ]

        recipe = Recipe(inputs, outputs, True)
        recipe_id = self._create_recipe(recipe)

        for output in outputs:
            if output.token_action == 0:
                if output.token_type == 20:
                    contract = MockErc20.MockErc20(output.token_address)
                    contract.mint(
                        self.crafting.address, output.amount, {"from": accounts[1]}
                    )
                elif output.token_type == 1155:
                    contract = MockERC1155.MockERC1155(output.token_address)
                    contract.mint(
                        self.crafting.address,
                        output.token_id,
                        output.amount,
                        b"",
                        {"from": accounts[1]},
                    )

        block_no_before = web3_client.eth.block_number

        with self.assertRaises(VirtualMachineError):
            self.crafting.craft(recipe_id, {"from": accounts[1]})

    def test_large_craft_with_all_types(self):
        inputs = []
        outputs = []

        inputs_size = 5
        outputs_size = 5
        erc1155_max_id = 10

        input_erc20_tokens = self.erc20_contracts[:5]
        input_erc1155_tokens = self.erc1155_contracts[:5]

        output_erc20_tokens = self.erc20_contracts[5:]
        output_erc1155_tokens = self.erc1155_contracts[5:]

        for erc20 in self.erc20_contracts:
            erc20.mint(
                self.crafting.address,
                10 ** 18 * 10 ** 18,
                {"from": accounts[0]},
            )
            erc20.mint(
                accounts[1],
                10 ** 18 * 10 ** 18,
                {"from": accounts[0]},
            )
            erc20.approve(
                self.crafting.address, 10 ** 18 * 10 ** 18, {"from": accounts[1]}
            )

        for erc1155 in self.erc1155_contracts:
            erc1155.mint_batch(
                self.crafting.address,
                [i for i in range(erc1155_max_id)],
                [10 ** 18 for i in range(erc1155_max_id)],
                b"",
                {"from": accounts[0]},
            )
            erc1155.mint_batch(
                accounts[1],
                [i for i in range(erc1155_max_id)],
                [10 ** 18 for i in range(erc1155_max_id)],
                b"",
                {"from": accounts[0]},
            )
            erc1155.set_approval_for_all(
                self.crafting.address, True, {"from": accounts[1]}
            )

        for i in range(inputs_size):
            token_type = 20 if i % 2 == 0 else 1155
            token_action = i % 3

            if token_type == 20:
                token = input_erc20_tokens[i % len(input_erc20_tokens)]
                amount = i * 10 ** 18
                inputs.append(
                    CraftingInput(
                        token_type,
                        token.address,
                        0,
                        amount,
                        token_action,
                    )
                )

            elif token_type == 1155:
                token = input_erc1155_tokens[i % len(input_erc1155_tokens)]
                amount = i
                token_id = i % erc1155_max_id
                inputs.append(
                    CraftingInput(
                        token_type,
                        token.address,
                        token_id,
                        amount,
                        token_action,
                    )
                )

        for i in range(1, outputs_size + 1):
            token_type = 20 if i % 2 == 0 else 1155
            token_action = i % 2

            if token_type == 20:
                token = output_erc20_tokens[i % len(output_erc20_tokens)]
                amount = (100 - i) * 10 ** 18
                outputs.append(
                    CraftingOutput(
                        token_type,
                        token.address,
                        0,
                        amount,
                        token_action,
                    )
                )
            elif token_type == 1155:
                token = output_erc1155_tokens[i % len(output_erc1155_tokens)]
                amount = (100 - i) * 2
                token_id = i % erc1155_max_id
                outputs.append(
                    CraftingOutput(
                        token_type,
                        token.address,
                        token_id,
                        amount,
                        token_action,
                    )
                )

        recipe = Recipe(inputs, outputs, True)
        recipe_id = self._create_recipe(recipe)

        block_no_before = web3_client.eth.block_number
        self.crafting.craft(recipe_id, {"from": accounts[1]})

        self._check_balances_after_crafting(recipe, block_no_before)
