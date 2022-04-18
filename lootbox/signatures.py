"""
Signing and signature verification functionality and interfaces.
"""
import abc

from brownie import accounts
from brownie.network import web3
from eth_account._utils.signing import sign_message_hash
import eth_keys
from hexbytes import HexBytes


class Signer:
    @abc.abstractmethod
    def sign_message(self, message):
        pass


class BrownieAccountSigner(Signer):
    """
    Simple implementation of a signer that uses a Brownie account to sign messages.
    """

    def __init__(self, keystore_file: str, password: str) -> None:
        self.signer = accounts.load(keystore_file, password)

    def sign_message(self, message):
        eth_private_key = eth_keys.keys.PrivateKey(HexBytes(self.signer.private_key))
        message_hash_bytes = HexBytes(message)
        _, _, _, signed_message_bytes = sign_message_hash(
            eth_private_key, message_hash_bytes
        )
        return signed_message_bytes.hex()


def get_signing_account(raw_message: str, signature: str) -> str:
    return web3.eth.account.recover_message(raw_message, signature=signature)
