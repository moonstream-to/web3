import time
import unittest

from brownie import network, accounts

from .auth import (
    authorize,
    verify,
    MoonstreamAuthorizationVerificationError,
    MoonstreamAuthorizationExpired,
)


class TestAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            network.connect()
        except:
            pass
        cls.signer = accounts.add()

    def test_authorization_and_verification(self):
        current_time = int(time.time())
        payload = authorize(current_time + 300, self.signer)
        self.assertDictContainsSubset(
            {"address": self.signer.address, "deadline": current_time + 300}, payload
        )
        self.assertTrue(verify(payload))

    def test_authorization_and_verification_fails_for_wrong_address(self):
        current_time = int(time.time())
        payload = authorize(current_time + 300, self.signer)
        payload["address"] = accounts[0].address
        with self.assertRaises(MoonstreamAuthorizationVerificationError):
            verify(payload)

    def test_authorization_and_verification_fails_after_deadline(self):
        current_time = int(time.time())
        payload = authorize(current_time - 1, self.signer)
        with self.assertRaises(MoonstreamAuthorizationExpired):
            verify(payload)


if __name__ == "__main__":
    unittest.main()
