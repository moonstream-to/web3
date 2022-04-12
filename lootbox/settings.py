import os

# Origin
RAW_ORIGINS = os.environ.get("MOONSTREAM_CORS_ALLOWED_ORIGINS")
if RAW_ORIGINS is None:
    raise ValueError(
        "MOONSTREAM_CORS_ALLOWED_ORIGINS environment variable must be set (comma-separated list of CORS allowed origins)"
    )
ORIGINS = RAW_ORIGINS.split(",")

# OpenAPI
DOCS_TARGET_PATH = "docs"

# AWS signer
AWS_REGION_NAME = os.environ.get("AWS_REGION_NAME")
if AWS_REGION_NAME is None:
    raise ValueError("AWS_REGION_NAME environment variable must be set")

AWS_SIGNER_LAUNCH_TEMPLATE_ID = os.environ.get("AWS_SIGNER_LAUNCH_TEMPLATE_ID")
if AWS_SIGNER_LAUNCH_TEMPLATE_ID is None:
    raise ValueError("AWS_SIGNER_LAUNCH_TEMPLATE_ID environment variable must be set")

AWS_SIGNER_IMAGE_ID = os.environ.get("AWS_SIGNER_IMAGE_ID")
if AWS_SIGNER_IMAGE_ID is None:
    raise ValueError("AWS_SIGNER_IMAGE_ID environment variable must be set")
