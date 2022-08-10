from typing import Any, Dict


from . import MockChainlinkCoordinator, MockLinkToken, MockVRFUser


def gogogo(tx_config: Dict[str, Any]):

    linkToken = MockLinkToken.MockLinkToken(None)
    linkToken.deploy(tx_config)

    chainlinkCoordinator = MockChainlinkCoordinator.MockChainlinkCoordinator(None)
    chainlinkCoordinator.deploy(linkToken.address, tx_config)

    return {
        "linkToken": linkToken.address,
        "chainlinkCoordinator": chainlinkCoordinator.address,
    }
