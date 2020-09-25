import logging
import boto3

logger = logging.getLogger()

def get_client(account_id, client_name, role_arn, region=None):
    # Get a boto3 client based on client_name (e.g. 'ec2')
    logger.debug("[get_client] account_id:{}, client_name:{}, region:{}".format(account_id, client_name, region))
    sts_client = boto3.client('sts')
    sts_response = sts_client.assume_role(RoleArn=role_arn,
                                          RoleSessionName="ConfigAssumedRole")
    args = dict(aws_access_key_id=sts_response['Credentials']['AccessKeyId'],
                aws_secret_access_key=sts_response['Credentials']['SecretAccessKey'],
                aws_session_token=sts_response['Credentials']['SessionToken'])
    if region is not None:
        args['region_name'] = region
    else:
        args['region_name'] = boto3.Session().region_name  # if not passed, get the current region we're running in
    return boto3.client(client_name, **args)

def get_iam_role_arn(account_id, role_name):
    return 'arn:aws:iam::{}:role/{}'.format(account_id, role_name)