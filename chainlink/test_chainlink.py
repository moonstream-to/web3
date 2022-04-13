import unittest

import json
from brownie.network import web3 as web3_client

from brownie import accounts, network
from brownie.exceptions import VirtualMachineError
from . import MockChainlinkCoordinator, MockLinkToken, MockVRFUser
from .mock_vrf_oracle import MockVRFOracle
from .core import gogogo


class TestChainlinkBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            network.connect()

        except:
            pass

        contracts = gogogo({"from": accounts[0]})
        cls.linkToken = MockLinkToken.MockLinkToken(contracts["linkToken"])
        cls.chainlinkCoordinator = MockChainlinkCoordinator.MockChainlinkCoordinator(
            contracts["chainlinkCoordinator"]
        )

        vrfFee = 0.01 * 10 ** 18
        vrfHash = "0xf86195cf7690c55907b2b611ebb7343a6f649bff128701cc542f0569e2c549da"
        cls.vrfUser = MockVRFUser.MockVRFUser(None)
        cls.vrfUser.deploy(
            cls.chainlinkCoordinator.address,
            cls.linkToken.address,
            vrfFee,
            vrfHash,
            {"from": accounts[0]},
        )

        cls.VRFOracle = MockVRFOracle(
            web3_client, cls.chainlinkCoordinator.address, accounts[0]
        )
        cls.linkToken.mint(cls.vrfUser.address, 10000 * 10 ** 18, {"from": accounts[0]})


class TestChainlink(TestChainlinkBase):
    def test_request(self):
        tx = self.vrfUser.request({"from": accounts[0]})

        requestId = tx.events["RandomnessRequest"]["requestID"]
        self.VRFOracle.fulfill_pending_requests()

        self.assertEquals(
            self.vrfUser.randomness_fullfilled(requestId),
            True,
        )

    def test_batch_fulfill_requests(self):
        txs = [self.vrfUser.request({"from": accounts[0]}) for _ in range(10)]
        requestIds = [tx.events["RandomnessRequest"]["requestID"] for tx in txs]

        self.VRFOracle.fulfill_pending_requests()

        for requestId in requestIds:
            self.assertEquals(
                self.vrfUser.randomness_fullfilled(requestId),
                True,
            )

    def test_request_with_custom_rng(self):
        tx = self.vrfUser.request({"from": accounts[0]})
        requestId = tx.events["RandomnessRequest"]["requestID"]

        self.VRFOracle.fulfill_pending_requests(lambda: 5)
        self.assertEquals(
            self.vrfUser.randomness_fullfilled(requestId),
            True,
        )
        self.assertEquals(
            self.vrfUser.randomness_value(requestId),
            5,
        )


if __name__ == "__main__":
    unittest.main()
