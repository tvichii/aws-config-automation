#!/usr/bin/env python3

from aws_cdk import core

from aws_config_automation.aws_config_automation_stack import AwsConfigAutomationStack


app = core.App()
AwsConfigAutomationStack(app, "aws-config-automation", env={'region': 'us-west-2'})

app.synth()
