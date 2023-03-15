import unittest

from brownie import accounts, network
from brownie.exceptions import VirtualMachineError
from brownie.network import web3 as web3_client

from . import ReentrancyExploitable, ExploitContract
from .core import diamond_gogogo, facet_cut


class ReentrancyGuardTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            network.connect()
        except:
            pass

        reentrancy_exploitable_gogogo_result = diamond_gogogo(
            accounts[0].address, {"from": accounts[0]}
        )
        cls.reentrancy_exploitable = ReentrancyExploitable.ReentrancyExploitable(
            reentrancy_exploitable_gogogo_result["contracts"]["Diamond"]
        )

        reentrancy_exploitable_facet = ReentrancyExploitable.ReentrancyExploitable(None)
        reentrancy_exploitable_facet.deploy({"from": accounts[0]})
        facet_cut(
            cls.reentrancy_exploitable.address,
            "ReentrancyExploitable",
            reentrancy_exploitable_facet.address,
            "add",
            {
                "from": accounts[0],
            },
        )

    def test_without_reentrancy_guard(self):
        exploit_contract = ExploitContract.ExploitContract(None)
        exploit_contract.deploy({"from": accounts[0]})
        exploit_contract.set_should_call_exploitable_function(
            True, {"from": accounts[0]}
        )
        exploit_contract.set_should_exploit(True, {"from": accounts[0]})

        curr_counter = self.reentrancy_exploitable.get_counter()

        exploit_contract.exploit(
            self.reentrancy_exploitable.address, {"from": accounts[0]}
        )

        self.assertEqual(
            exploit_contract.did_exploit(),
            True,
        )

        self.assertEqual(
            self.reentrancy_exploitable.get_counter(),
            curr_counter + 2,
        )

    def test_with_reentrancy_guard_exploit_fails(self):
        exploit_contract = ExploitContract.ExploitContract(None)
        exploit_contract.deploy({"from": accounts[0]})
        exploit_contract.set_should_call_exploitable_function(
            False, {"from": accounts[0]}
        )
        exploit_contract.set_should_exploit(True, {"from": accounts[0]})

        curr_counter = self.reentrancy_exploitable.get_counter()

        with self.assertRaises(VirtualMachineError):
            exploit_contract.exploit(
                self.reentrancy_exploitable.address, {"from": accounts[0]}
            )

        self.assertEqual(
            exploit_contract.did_exploit(),
            False,
        )

        self.assertEqual(
            self.reentrancy_exploitable.get_counter(),
            curr_counter,
        )

    def test_with_reentrancy_guard_without_exploit(self):
        exploit_contract = ExploitContract.ExploitContract(None)
        exploit_contract.deploy({"from": accounts[0]})
        exploit_contract.set_should_call_exploitable_function(
            False, {"from": accounts[0]}
        )
        exploit_contract.set_should_exploit(False, {"from": accounts[0]})

        curr_counter = self.reentrancy_exploitable.get_counter()

        exploit_contract.exploit(
            self.reentrancy_exploitable.address, {"from": accounts[0]}
        )

        self.assertEqual(
            exploit_contract.did_exploit(),
            False,
        )

        self.assertEqual(
            self.reentrancy_exploitable.get_counter(),
            curr_counter + 1,
        )


if __name__ == "__main__":
    unittest.main()
