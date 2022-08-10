import os
from typing import Dict
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware


# Origin
RAW_ORIGINS = os.environ.get("ENGINE_CORS_ALLOWED_ORIGINS")
if RAW_ORIGINS is None:
    raise ValueError(
        "ENGINE_CORS_ALLOWED_ORIGINS environment variable must be set (comma-separated list of CORS allowed origins)"
    )
ORIGINS = RAW_ORIGINS.split(",")

ENGINE_BROWNIE_NETWORK = os.environ.get("ENGINE_BROWNIE_NETWORK")
if ENGINE_BROWNIE_NETWORK is None:
    raise ValueError("ENGINE_BROWNIE_NETWORK environment variable must be set")

ENGINE_DROPPER_ADDRESS = os.environ.get("ENGINE_DROPPER_ADDRESS")
if ENGINE_DROPPER_ADDRESS is None:
    raise ValueError("ENGINE_DROPPER_ADDRESS environment variable must be set")

SIGNER_KEYSTORE = os.environ.get("SIGNER_KEYSTORE")
SIGNER_PASSWORD = os.environ.get("SIGNER_PASSWORD")

MOONSTREAM_SIGNING_SERVER_IP = os.environ.get("MOONSTREAM_SIGNING_SERVER_IP", None)


DOCS_TARGET_PATH = os.environ.get("DOCS_TARGET_PATH", "docs")


# AWS signer
AWS_DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION")
if AWS_DEFAULT_REGION is None:
    raise ValueError("AWS_DEFAULT_REGION environment variable must be set")

MOONSTREAM_AWS_SIGNER_LAUNCH_TEMPLATE_ID = os.environ.get(
    "MOONSTREAM_AWS_SIGNER_LAUNCH_TEMPLATE_ID"
)
if MOONSTREAM_AWS_SIGNER_LAUNCH_TEMPLATE_ID is None:
    raise ValueError(
        "MOONSTREAM_AWS_SIGNER_LAUNCH_TEMPLATE_ID environment variable must be set"
    )

MOONSTREAM_AWS_SIGNER_IMAGE_ID = os.environ.get("MOONSTREAM_AWS_SIGNER_IMAGE_ID")
if MOONSTREAM_AWS_SIGNER_IMAGE_ID is None:
    raise ValueError("MOONSTREAM_AWS_SIGNER_IMAGE_ID environment variable must be set")

MOONSTREAM_AWS_SIGNER_INSTANCE_PORT = 17181

# Blockchain configuration

ETHEREUM_PROVIDER_URI = os.environ.get("MOONSTREAM_ETHEREUM_WEB3_PROVIDER_URI")
MUMBAI_PROVIDER_URI = os.environ.get("MOONSTREAM_MUMBAI_WEB3_PROVIDER_URI")
POLYGON_PROVIDER_URI = os.environ.get("MOONSTREAM_POLYGON_WEB3_PROVIDER_URI")
XDAI_PROVIDER_URI = os.environ.get("MOONSTREAM_XDAI_WEB3_PROVIDER_URI")

NODEBALANCER_ACCESS_ID = os.environ.get("ENGINE_NODEBALANCER_ACCESS_ID")
if NODEBALANCER_ACCESS_ID is not None:
    NODEBALANCER_URI_TEMPLATE = (
        "https://nb.moonstream.to/nb/{}/jsonrpc?access_id={}&data_source=blockchain"
    )
    ETHEREUM_PROVIDER_URI = NODEBALANCER_URI_TEMPLATE.format(
        "ethereum", NODEBALANCER_ACCESS_ID
    )
    MUMBAI_PROVIDER_URI = NODEBALANCER_URI_TEMPLATE.format(
        "mumbai", NODEBALANCER_ACCESS_ID
    )
    POLYGON_PROVIDER_URI = NODEBALANCER_URI_TEMPLATE.format(
        "polygon", NODEBALANCER_ACCESS_ID
    )
    XDAI_PROVIDER_URI = NODEBALANCER_URI_TEMPLATE.format("xdai", NODEBALANCER_ACCESS_ID)

BLOCKCHAIN_PROVIDER_URIS = {
    "ethereum": ETHEREUM_PROVIDER_URI,
    "mumbai": MUMBAI_PROVIDER_URI,
    "polygon": POLYGON_PROVIDER_URI,
    "xdai": XDAI_PROVIDER_URI,
}

SUPPORTED_BLOCKCHAINS = ", ".join(BLOCKCHAIN_PROVIDER_URIS)
UNSUPPORTED_BLOCKCHAIN_ERROR_MESSAGE = f"That blockchain is not supported. The supported blockchains are: {SUPPORTED_BLOCKCHAINS}."

BLOCKCHAIN_WEB3_PROVIDERS = {
    blockchain: Web3(HTTPProvider(jsonrpc_uri))
    for blockchain, jsonrpc_uri in BLOCKCHAIN_PROVIDER_URIS.items()
}

# For Proof-of-Authority chains (e.g. Polygon), inject the geth_poa_middleware into the web3 client:
# https://web3py.readthedocs.io/en/stable/middleware.html#geth-style-proof-of-authority
# For every chain represented in BLOCKCHAIN_WEB3_PROVIDERS and BLOCKCHAIN_PROVIDER_URIS, if the chain
# is a proof-of-authority chain, add it to the POA_CHAINS list, as well.
POA_CHAINS = ["mumbai", "polygon"]
for chain in POA_CHAINS:
    BLOCKCHAIN_WEB3_PROVIDERS[chain].middleware_onion.inject(
        geth_poa_middleware, layer=0
    )
