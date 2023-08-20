import argparse
import logging
import os
from datetime import datetime

import boto3
from botocore.config import Config

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


def generate_presigned_url(bucket: str, key: str):
    client_method = 'put_object'

    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
        # config=Config(signature_version='s3v4'),
        region_name='ap-northeast-2',
        endpoint_url='https://s3.ap-northeast-2.amazonaws.com'
    )

    url = s3_client.generate_presigned_url(
        ClientMethod=client_method,
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=1000
    )
    return url
