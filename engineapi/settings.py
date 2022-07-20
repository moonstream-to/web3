import os
from typing import Dict


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
# OpenAPI
DOCS_TARGET_PATH_OPENAPI = {
    "dropper": "docs/dropper",
    "leaderboard": "docs/leaderboard",
    "admin": "docs/admin",
    "play": "docs/play"
}

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

BLOCKCHAINS_TO_BROWNIE_NETWORKS: Dict[str, str] = {
    "polygon": "moonstream-engine-polygon",
    "mumbai": "mumbai",
}
