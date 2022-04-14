"""
IMPORTANT NOTES

Be aware of running and terminating instances at AWS.
For proper use environment variables prod.test.env should be specified.

For 
"""
import os
import unittest

from . import signatures


class RunTerminateInstancesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.TEST_AWS_WRONG_INSTANCE_ID = os.environ.get("TEST_AWS_WRONG_INSTANCE_ID")
        if cls.TEST_AWS_WRONG_INSTANCE_ID is None:
            raise ValueError(
                "TEST_AWS_WRONG_INSTANCE_ID environment variable must be set"
            )


class WakeupInstancesTestCase(RunTerminateInstancesTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.TEST_AWS_WAKEUP_INSTANCES_TO_TEARDOWN = []

    def test_run_instances_dry_run(self):
        run_instances_0 = signatures.wakeup_instances()
        self.assertListEqual([], run_instances_0)

        with self.assertRaises(signatures.AWSRunInstancesFail):
            signatures.wakeup_instances(True)

        with self.assertRaises(signatures.AWSRunInstancesFail):
            signatures.wakeup_instances(True, True)

    def test_run_instances(self):
        run_instances_0 = signatures.wakeup_instances(True, False)
        self.assertEqual(1, len(run_instances_0))
        self.TEST_AWS_WAKEUP_INSTANCES_TO_TEARDOWN.extend(run_instances_0)

    @classmethod
    def tearDownClass(cls) -> None:
        signatures.sleep_instances(cls.TEST_AWS_WAKEUP_INSTANCES_TO_TEARDOWN)


class SleepInstancesTestCase(RunTerminateInstancesTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.TEST_AWS_INSTANCE_ID_FIRST = signatures.wakeup_instances(True, False)[0]
        cls.TEST_AWS_INSTANCE_ID_SECOND = signatures.wakeup_instances(True, False)[0]

    def test_empty_signing_instances(self):
        with self.assertRaises(signatures.SigningInstancesNotFound):
            signatures.sleep_instances([])
        with self.assertRaises(signatures.SigningInstancesNotFound):
            signatures.sleep_instances([], True)

    def test_wrong_instance_id(self):
        with self.assertRaises(signatures.AWSDescribeInstancesFail):
            signatures.sleep_instances(["i-unexisting"])
        with self.assertRaises(signatures.AWSDescribeInstancesFail):
            signatures.sleep_instances(["i-unexisting", "i-test"])
        with self.assertRaises(signatures.AWSDescribeInstancesFail):
            signatures.sleep_instances(["i-unexisting"], True)

    def test_described_instances_not_found(self):
        with self.assertRaises(signatures.SigningInstancesNotFound):
            signatures.sleep_instances([self.TEST_AWS_WRONG_INSTANCE_ID])
        with self.assertRaises(signatures.SigningInstancesNotFound):
            signatures.sleep_instances([self.TEST_AWS_WRONG_INSTANCE_ID], True)
        with self.assertRaises(signatures.SigningInstancesTerminationLimitExceeded):
            signatures.sleep_instances(
                [
                    self.TEST_AWS_INSTANCE_ID_FIRST,
                    self.TEST_AWS_INSTANCE_ID_SECOND,
                ]
            )
        with self.assertRaises(signatures.SigningInstancesTerminationLimitExceeded):
            signatures.sleep_instances(
                [
                    self.TEST_AWS_INSTANCE_ID_FIRST,
                    self.TEST_AWS_INSTANCE_ID_SECOND,
                ],
                True,
            )

    def test_terminate_instances_dry_run(self):
        with self.assertRaises(signatures.AWSTerminateInstancesFail):
            signatures.sleep_instances([self.TEST_AWS_INSTANCE_ID_FIRST], True)

    def test_terminate_instances(self):
        terminated_instances_0 = signatures.sleep_instances(
            [self.TEST_AWS_INSTANCE_ID_FIRST], True, False
        )
        self.assertListEqual([self.TEST_AWS_INSTANCE_ID_FIRST], terminated_instances_0)

    @classmethod
    def tearDownClass(cls) -> None:
        signatures.sleep_instances([cls.TEST_AWS_INSTANCE_ID_SECOND], True, False)
