import datetime
from typing import List, Any

import pytz
from botocore.exceptions import ClientError

from boto3 import session
import boto3

__author__ = "Dheeraj Banodha"
__version__ = '0.3.6'

import logging

from aws_recommendation.cloudwatch import cloudwatch
from aws_recommendation.dynamodb import dynamodb
from aws_recommendation.ebs import ebs
from aws_recommendation.ec2 import ec2
from aws_recommendation.elb import elb
from aws_recommendation.kms import kms
from aws_recommendation.rds import rds
from aws_recommendation.redshift import redshift
from aws_recommendation.s3 import s3
from aws_recommendation.utils import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class aws_client(utils, cloudwatch, s3, rds, ec2, dynamodb, ebs, elb, kms, redshift):
    def __init__(self, **kwargs):
        if 'aws_access_key_id' in kwargs.keys() and 'aws_secret_access_key' in kwargs.keys():
            if 'iam_role_to_assume' in kwargs.keys():
                self.iam_role_to_assume = kwargs['iam_role_to_assume']
                self.sts_client = boto3.client(
                    'sts',
                    aws_access_key_id=kwargs['aws_access_key_id'],
                    aws_secret_access_key=kwargs['aws_secret_access_key'],
                )
                self.creds = self.sts_client.assume_role(
                    RoleArn=self.iam_role_to_assume,
                    RoleSessionName='RecommenderSession',
                    DurationSeconds=3600
                )
                self.session = session.Session(
                    aws_access_key_id=self.creds['Credentials']['AccessKeyId'],
                    aws_secret_access_key=self.creds['Credentials']['SecretAccessKey'],
                    aws_session_token=self.creds['Credentials']['SessionToken']
                )
            else:
                self.session = session.Session(
                    aws_access_key_id=kwargs['aws_access_key_id'],
                    aws_secret_access_key=kwargs['aws_secret_access_key'],
                )
        elif 'profile_name' in kwargs.keys():
            self.session = session.Session(profile_name=kwargs['profile_name'])
        elif 'iam_role_to_assume' in kwargs.keys():
            self.iam_role_to_assume = kwargs['iam_role_to_assume']
            self.sts_client = boto3.client('sts')
            self.creds = self.sts_client.assume_role(
                RoleArn=kwargs['iam_role_to_assume'],
                RoleSessionName='RecommenderSession',
                DurationSeconds=3600
            )
            self.session = session.Session(
                aws_access_key_id=self.creds['Credentials']['AccessKeyId'],
                aws_secret_access_key=self.creds['Credentials']['SecretAccessKey'],
                aws_session_token=self.creds['Credentials']['SessionToken']
            )

    from .cost_estimations import estimated_savings

    # refresh session
    def refresh_session(self):
        try:
            self.sts_client
        except AttributeError:
            logger.info('No need to refresh the session!')
            return
        remaining_duration_seconds = (
                self.creds['Credentials']['Expiration'] - datetime.datetime.now(pytz.utc)).total_seconds()

        if remaining_duration_seconds < 900:
            self.creds = self.sts_client.assume_role(
                RoleArn=self.iam_role_to_assume,
                RoleSessionName='RecommenderSession',
                DurationSeconds=3600
            )
            self.session = session.Session(
                aws_access_key_id=self.creds['Credentials']['AccessKeyId'],
                aws_secret_access_key=self.creds['Credentials']['SecretAccessKey'],
                aws_session_token=self.creds['Credentials']['SessionToken']
            )


    # Merge the recommendations and return the list
    def get_recommendations(self) -> list:
        recommendations: list[Any] = []
        regions = self.get_regions()

        ec2_instances = self.list_instances(regions)

        recommendations += self.get_s3_recommendations()
        recommendations += self.get_cw_recommendations(regions=regions)
        recommendations += self.get_rds_recommendations(regions=regions)
        recommendations += self.get_ec2_recommendations(regions=regions, ec2_instances=ec2_instances)
        recommendations += self.get_dynamodb_recommendations(regions=regions)
        recommendations += self.estimated_savings(regions=regions, ec2_instances=ec2_instances)
        recommendations += self.get_ebs_recommendations(regions=regions)
        recommendations += self.get_elb_recommendations(regions)
        recommendations += self.get_kms_recommendations(regions)
        recommendations += self.get_redshift_recommendations(regions)

        return recommendations




