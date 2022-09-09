import unittest

from brownie import accounts, network

from . import GOFPFacet
from .core import gofp_gogogo, ZERO_ADDRESS


class GOFPTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            network.connect()
        except:
            pass

        cls.owner = accounts[0]
        cls.owner_tx_config = {"from": cls.owner}

        cls.deployed_contracts = gofp_gogogo(ZERO_ADDRESS, 0, cls.owner_tx_config)
        cls.gofp = GOFPFacet.GOFPFacet(cls.deployed_contracts["contracts"]["Diamond"])


class TestGOFPDeployment(GOFPTestCase):
    def test_gofp_deployment(self):
        terminus_info = self.gofp.admin_terminus_info()
        self.assertEqual(terminus_info[0], ZERO_ADDRESS)
        self.assertEqual(terminus_info[1], 0)


if __name__ == "__main__":
    unittest.main()
