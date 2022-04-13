import logging
from typing import List

import boto3

from .settings import (
    AWS_DEFAULT_REGION,
    MOONSTREAM_AWS_SIGNER_LAUNCH_TEMPLATE_ID,
    MOONSTREAM_AWS_SIGNER_IMAGE_ID,
)

logger = logging.getLogger(__name__)

aws_client = boto3.client("ec2", region_name=AWS_DEFAULT_REGION)


class AWSDescribeInstancesFail(Exception):
    """
    Raised when AWS describe instances command failed.
    """


class AWSRunInstancesFail(Exception):
    """
    Raised when AWS run instances command failed.
    """


class AWSTerminateInstancesFail(Exception):
    """
    Raised when AWS terminate instances command failed.
    """


class SigningInstancesNotFound(Exception):
    """
    Raised when signing instances with the given ids is not found in at AWS.
    """


class SigningInstancesTerminationLimitExceeded(Exception):
    """
    Raised when provided several instances to termination.
    """


def wakeup_instances(run_confirmed=False, dry_run=True) -> List[str]:
    """
    Run new signing instances.
    """
    run_instances = []
    if run_confirmed:
        try:
            run_instances_response = aws_client.run_instances(
                LaunchTemplate={
                    "LaunchTemplateId": MOONSTREAM_AWS_SIGNER_LAUNCH_TEMPLATE_ID
                },
                MinCount=1,
                MaxCount=1,
                DryRun=dry_run,
            )
            for i in run_instances_response["Instances"]:
                run_instances.append(i["InstanceId"])
        except Exception as err:
            logger.error(f"AWS run instances command failed: {err}")
            raise AWSRunInstancesFail("AWS run instances command failed")

    return run_instances


def sleep_instances(
    signing_instances: List[str], termination_confirmed=False, dry_run=True
) -> List[str]:
    """
    Fetch, describe, verify signing instances and terminate them.
    """
    if len(signing_instances) == 0:
        raise SigningInstancesNotFound("There are no signing instances to describe")

    described_instances = []
    try:
        described_instances_response = aws_client.describe_instances(
            Filters=[{"Name": "image-id", "Values": [MOONSTREAM_AWS_SIGNER_IMAGE_ID]}],
            InstanceIds=signing_instances,
        )
        for r in described_instances_response["Reservations"]:
            for i in r["Instances"]:
                described_instances.append(i["InstanceId"])
    except Exception as err:
        logger.error(f"AWS describe instances command failed: {err}")
        raise AWSDescribeInstancesFail("AWS describe instances command failed.")

    if len(described_instances) == 0:
        raise SigningInstancesNotFound(
            "Signing instances with the given ids is not found in at AWS."
        )
    if len(described_instances) > 1:
        raise SigningInstancesTerminationLimitExceeded(
            f"Provided {len(described_instances)} instances to termination"
        )

    terminated_instances = []
    if termination_confirmed:
        try:
            terminated_instances_response = aws_client.terminate_instances(
                InstanceIds=described_instances,
                DryRun=dry_run,
            )
            for i in terminated_instances_response["TerminatingInstances"]:
                terminated_instances.append(i["InstanceId"])
        except Exception as err:
            logger.error(
                f"Unable to terminate instance {described_instances}, error: {err}"
            )
            raise AWSTerminateInstancesFail("AWS terminate instances command failed")

    return terminated_instances
