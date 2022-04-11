"""
Lootbox API.
"""
import logging

import boto3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import data
from .middleware import MoonstreamHTTPException
from .settings import (
    DOCS_TARGET_PATH,
    ORIGINS,
)

signer_instances = []

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

aws_client = boto3.client("ec2", region_name="<region_name>")

tags_metadata = [
    {"name": "test", "description": "Test."},
]

app = FastAPI(
    title=f"Lootbox HTTP API",
    description="Lootbox API endpoints.",
    version="v0.0.1",
    openapi_tags=tags_metadata,
    openapi_url="/openapi.json",
    docs_url=None,
    redoc_url=f"/{DOCS_TARGET_PATH}",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping", response_model=data.PingResponse)
async def ping_handler() -> data.PingResponse:
    """
    Check server status.
    """
    return data.PingResponse(status="ok")


@app.get("/wakeup", response_model=data.WakeupResponse)
async def wakeup_handler():
    global signer_instance
    try:
        response = aws_client.run_instances(
            LaunchTemplate={"LaunchTemplateId": "<lt_id>"},
            MinCount=1,
            MaxCount=1,
            DryRun=True,
        )
        signer_instances.extend(response["Instances"])
    except Exception as err:
        logger.error(f"Unhandled /wakeup exception, error: {err}")
        raise MoonstreamHTTPException(status_code=500)

    return data.SleepResponse(instances=signer_instances)


@app.get("/sleep", response_model=data.SleepResponse)
async def sleep_handler():
    try:
        instance_ids = [i["InstanceId"] for i in signer_instances]
        response = aws_client.terminate_instances(
            InstanceIds=instance_ids,
            DryRun=True,
        )
    except Exception as err:
        logger.error(f"Unhandled /wakeup exception, error: {err}")
        raise MoonstreamHTTPException(status_code=500)

    return data.SleepResponse(instances=signer_instances)
