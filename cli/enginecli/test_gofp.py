import unittest

from brownie import accounts, network

from . import GOFPFacet
from .core import diamond_gogogo, Diamond, facet_cut


class GOFPTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            network.connect()
        except:
            pass

        cls.owner = accounts[0]
        cls.owner_tx_config = {"from": cls.owner}

        cls.deployed_contracts = diamond_gogogo(
            accounts[0].address, cls.owner_tx_config
        )

        cls.diamond = Diamond.Diamond(cls.deployed_contracts["Diamond"])

        gofp_facet = GOFPFacet.GOFPFacet(None)
        gofp_facet.deploy(cls.owner_tx_config)

        cls.deployed_contracts["GOFPFacet"] = gofp_facet.address

        facet_cut(cls.diamond.address, "GOFPFacet")


if __name__ == "__main__":
    unittest.main()
