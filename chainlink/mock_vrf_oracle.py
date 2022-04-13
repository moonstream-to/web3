import random
from eth_typing import ChecksumAddress
from moonworm.crawler.log_scanner import _fetch_events_chunk
from brownie import network

from .MockChainlinkCoordinator import MockChainlinkCoordinator
from moonworm.crawler.log_scanner import _fetch_events_chunk

abi = [
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "keyHash",
                "type": "bytes32",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "seed",
                "type": "uint256",
            },
            {
                "indexed": True,
                "internalType": "bytes32",
                "name": "jobID",
                "type": "bytes32",
            },
            {
                "indexed": False,
                "internalType": "address",
                "name": "sender",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "fee",
                "type": "uint256",
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "requestID",
                "type": "bytes32",
            },
        ],
        "name": "RandomnessRequest",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "requestId",
                "type": "bytes32",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "output",
                "type": "uint256",
            },
        ],
        "name": "RandomnessRequestFulfilled",
        "type": "event",
    },
]


def _generate_random_number():
    return random.randint(0, 2 ** 256)


class MockVRFOracle:
    def __init__(
        self,
        web3_client,
        coordinator_address: ChecksumAddress,
        signer,
        start_block: int = 0,
    ):
        self.last_block = start_block - 1
        self.chainlink_coordinator = MockChainlinkCoordinator(coordinator_address)
        self.signer = signer
        self.web3_client = web3_client

    def fulfill_pending_requests(self, rng=_generate_random_number):
        current_block_number = self.web3_client.eth.block_number
        events = _fetch_events_chunk(
            self.web3_client,
            abi[0],
            self.last_block + 1,
            current_block_number,
            [self.chainlink_coordinator.address],
        )
        self.last_block = current_block_number

        for event in events:
            self.chainlink_coordinator.mock_fulfill_randomness_request(
                event["args"]["requestID"],
                rng(),
                event["args"]["sender"],
                {"from": self.signer},
            )
