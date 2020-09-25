import aws_helper
import logging
import json
from config_bucket_policy import conf_bucket_policy

LOGGER = logging.getLogger()
def main(event, context):
    """
    Setup AWS Config for given tenant_id and all given regions for that tenant.
    :param event:
    :param context:
    :return:
    """
    tenant_id = "313517949584"
    regions = ["ap-south-1"]

    # Create S3 bucket for given tenant.
    iam_role_arn = aws_helper.get_iam_role_arn(tenant_id, 'ConfigRole')
    s3_client = aws_helper.get_client(tenant_id, 's3', iam_role_arn)
    s3_bucket = find_or_create_config_bucket(s3_client, tenant_id)

    for region in regions:
        config_client = aws_helper.get_client(tenant_id, 'config', role_arn=iam_role_arn, region=region)
        sns_client = aws_helper.get_client(tenant_id, 'sns', role_arn=iam_role_arn, region=region)

        # Create SNS Topic for given tenant region.
        sns = find_or_create_sns_topic(sns_client, tenant_id, region)

        # Setup Configuration Recorder for given tenant region.
        setup_config_recorder(config_client, tenant_id, region, iam_role_arn)

        # Setup Delivery Channel for given tenant region.
        setup_delivery_channel(config_client, tenant_id, region, s3_bucket, sns['TopicArn'])

        # Start Configuration Recorder.
        start_config_recorder(config_client, tenant_id, region)

def find_or_create_config_bucket(s3_client, tenant_id):
    """
    Finds or creates a s3 bucket for AWS Config for a tenant and returns the bucket name.
    :param s3_client:
    :param tenant_id:
    :return s3 bucket name:
    """
    try:
        LOGGER.info("Looking for a config bucket for Tenant [%s]...", tenant_id)
        response = s3_client.create_bucket(Bucket='config-bucket-' + tenant_id)
        LOGGER.info("Config bucket created for Tenant [%s], adding bucket policy...", tenant_id)

        policy_string = json.dumps(conf_bucket_policy)
        policy = policy_string.replace("tenant_id", tenant_id)
        s3_client.put_bucket_policy(
            Bucket='config-bucket-' + tenant_id,
            Policy=policy
        )
        LOGGER.info("Added config bucket policy to bucket config-bucket-[%s]", tenant_id)

        return 'config-bucket-' + tenant_id

    except Exception as ex:
        LOGGER.error("Error creating S3 bucket on tenant:[%s] \n [%s]", tenant_id, ex)
        raise

def find_or_create_sns_topic(sns_client, tenant_id, region):
    """
    Finds or creates a sns topic for the AWS Config delivery channel for a given tenant region.
    :param sns_client:
    :param tenant_id:
    :param region:
    :return sns_response:
    """
    try:
        LOGGER.info("Looking for a SNS topic for the AWS Config delivery channel on tenant [%s] in region [%s]", region,
                    tenant_id)
        sns_response = sns_client.create_topic(
            Name='config-topic-'+tenant_id+'-'+region,
        )
        LOGGER.info("SNS topic created for the config delivery channel on tenant:[%s] in region: [%s]", tenant_id,
                    region)
        return sns_response

    except Exception as ex:
        LOGGER.error(
            "Error while creating sns on tenant:[%s] in region: [%s] \n [%s]", tenant_id, region, ex)
        raise

def setup_config_recorder(config_client, tenant_id, region, role):
    """
    Setup a config recorder for the AWS Config delivery channel for a given tenant region.
    :param config_client:
    :param tenant_id:
    :param region:
    :param role:
    :return :
    """
    try:
        LOGGER.info("Setting up configuration recorder on tenant [%s] in region [%s]", tenant_id, region)
        response = config_client.put_configuration_recorder(
            ConfigurationRecorder={
                'name': 'default',
                'roleARN': role,
                'recordingGroup': {
                    'allSupported': True,
                    'includeGlobalResourceTypes': True,
                    'resourceTypes': []
                }
            }
        )
        LOGGER.info("Configuration Recorder setup on tenant:[%s] in region: [%s].", tenant_id, region)

    except Exception as ex:
        LOGGER.error("Error while creating configuration_recorder on tenant:[%s] in region: [%s] \n [%s].", tenant_id,
                     region, ex)
        raise

def setup_delivery_channel(config_client, tenant_id, region, s3_bucket, sns_topic):
    """
    Sets up a delivery channel for a given tenant region.
    :param config_client:
    :param tenant_id:
    :param region:
    :param s3_bucket:
    :param sns_topic:
    :return :
    """
    try:
        LOGGER.info("Setting up delivery channel on the tenant [%s] in region [%s]", tenant_id, region)
        response = config_client.put_delivery_channel(
            DeliveryChannel={
                'name': 'default',
                's3BucketName': s3_bucket,
                'snsTopicARN': sns_topic,
                'configSnapshotDeliveryProperties': {
                    'deliveryFrequency': 'TwentyFour_Hours'
                }
            }
        )
        LOGGER.info("Delivery channel setup on tenant:[%s] in region: [%s]", tenant_id, region)

    except Exception as ex:
        LOGGER.error("Error while creating delivery_channel on tenant:[%s] in region: [%s] \n [%s]", tenant_id, region,
                     ex)
        raise

def start_config_recorder(config_client, tenant_id, region):
    """
        Starts the config recorder on tenant region.
        :param config_client:
        :param tenant_id:
        :param region:
        :return :
        """
    try:
        LOGGER.info("Starting the configuration recorder...")
        status = config_client.start_configuration_recorder(
            ConfigurationRecorderName='default'
        )
        LOGGER.info("Successfully started the configuration recorder on tenant [%s] in region [%s]", tenant_id, region)

    except Exception as ex:
        LOGGER.error("Error while starting configuration_recorder on tenant:[%s] in region: [%s] \n [%s].", tenant_id,
                     region, ex)
        raise