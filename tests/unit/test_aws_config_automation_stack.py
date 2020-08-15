import json
import pytest

from aws_cdk import core
from aws-config-automation.aws_config_automation_stack import AwsConfigAutomationStack


def get_template():
    app = core.App()
    AwsConfigAutomationStack(app, "aws-config-automation")
    return json.dumps(app.synth().get_stack("aws-config-automation").template)


def test_sqs_queue_created():
    assert("AWS::SQS::Queue" in get_template())


def test_sns_topic_created():
    assert("AWS::SNS::Topic" in get_template())
