#!/usr/bin/env python3
import os
from aws_cdk import core

from aws_config_automation.aws_config_automation_stack import AwsConfigAutomationStack

STAGE = os.getenv('STAGE', 'dev')

app = core.App()
AwsConfigAutomationStack(app, "aws-config-automation", env={'region': 'us-east-1'},
                         environment={
                             'STAGE': STAGE
                         }
                         )

app.synth()
