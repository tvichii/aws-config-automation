import os
from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as _iam,
    # aws_sqs as sqs,
    # aws_sns as sns,
    # aws_sns_subscriptions as subs,
    core
)

STAGE = os.getenv('STAGE', 'dev')
DEFAULT_MEMORY_SIZE_LAMBDA_FUNCTION = 256

class AwsConfigAutomationStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str,environment: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        layer = _lambda.LayerVersion(
            self,
            'config-helper',
            code=_lambda.Code.asset('layer'),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_6],
            description='Helper functionns for config',
            layer_version_name='helper'
        )
        # Create config-setup-# Lambda resource
        lambda_config_setup = _lambda.Function(
            self,
            'lambda_function_config-setup-',
            runtime=_lambda.Runtime.PYTHON_3_6,
            code=_lambda.Code.asset('lambda'),
            handler='config-setup.main',
            function_name='config-setup-' + STAGE,
            memory_size=DEFAULT_MEMORY_SIZE_LAMBDA_FUNCTION,
            layers=[layer],
            environment=environment,
            timeout=core.Duration.seconds(900)
        )
        config_role_statement = _iam.PolicyStatement(
            actions=['sts:AssumeRole'],
            effect=_iam.Effect.ALLOW,
            resources=["arn:aws:iam::*:role/ConfigRole"]
        )
        lambda_config_setup.add_to_role_policy(config_role_statement)
