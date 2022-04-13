"""
Lootbox API.
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import data
from . import actions
from .middleware import MoonstreamHTTPException
from .settings import (
    AWS_REGION_NAME,
    MOONSTREAM_AWS_SIGNER_LAUNCH_TEMPLATE_ID,
    MOONSTREAM_AWS_SIGNER_IMAGE_ID,
    DOCS_TARGET_PATH,
    ORIGINS,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    try:
        run_instances = actions.wakeup_instances(run_confirmed=True, dry_run=True)
    except actions.AWSRunInstancesFail:
        raise MoonstreamHTTPException(status_code=500)
    except Exception as err:
        logger.error(f"Unhandled /wakeup exception: {err}")
        raise MoonstreamHTTPException(status_code=500)

    return data.WakeupResponse(instances=run_instances)


@app.get("/sleep", response_model=data.SleepResponse)
async def sleep_handler():
    try:
        terminated_instances = actions.sleep_instances(
            signing_instances=actions.SIGNING_INSTANCES,
            termination_confirmed=True,
            dry_run=True,
        )
    except actions.AWSDescribeInstancesFail:
        raise MoonstreamHTTPException(status_code=500)
    except actions.SigningInstancesNotFound:
        raise MoonstreamHTTPException(
            status_code=404, detail="There are no instances to terminate"
        )
    except actions.SigningInstancesTerminationLimitExceeded:
        raise MoonstreamHTTPException(
            status_code=403,
            detail="Could not be terminated several instances per operation",
        )
    except actions.AWSTerminateInstancesFail:
        raise MoonstreamHTTPException(status_code=500)
    except Exception as err:
        logger.error(f"Unhandled /sleep exception: {err}")
        raise MoonstreamHTTPException(status_code=500)

    return data.SleepResponse(instances=terminated_instances)
