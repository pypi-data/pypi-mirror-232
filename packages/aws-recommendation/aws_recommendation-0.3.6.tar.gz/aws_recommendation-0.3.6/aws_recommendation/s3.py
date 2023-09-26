import traceback

from botocore.exceptions import ClientError

from aws_recommendation.utils import *

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class s3:
    def get_s3_recommendations(self) -> list:
        """
        :return: list of s3 recommendations
        """
        bucket_list = self.__list_s3_buckets()
        return self.__enable_s3_bucket_keys(bucket_list) + self.__s3_bucket_versioning_enabled(bucket_list) + self.__s3_bucket_lifecycle_configuration(bucket_list)

    # returns the list of s3 buckets
    def __list_s3_buckets(self):
        """
        :return:
        """
        logger.info(" ---Inside utils :: list_s3_buckets()--- ")
        self.refresh_session()
        client = self.session.client('s3')

        try:
            response = client.list_buckets()
            return response['Buckets']
        except ClientError as e:
            return e.response['Error']['Code']

    # Generate the recommendation for enable s3 bucket keys
    def __enable_s3_bucket_keys(self, bucket_list: list) -> list:
        """
        :param bucket_list:
        :param self:
        :return:
        """
        logger.info(" ---Inside s3 :: enable_s3_bucket_keys()")
        self.refresh_session()

        recommendation = []

        client = self.session.client('s3')

        for bucket in bucket_list:
            try:
                res = client.get_bucket_encryption(
                    Bucket=bucket['Name']
                )
            except ClientError as e:
                if e.response['Error']['Code'] == 'AccessDenied':
                    logger.info('---------S3 read access denied----------')
                    temp = {
                        'Service Name': 'S3',
                        'Id': bucket['Name'],
                        'Recommendation': 'Access Denied',
                        'Description': 'Access Denied',
                        'Metadata': {
                            'Access Denied'
                        },
                        'Recommendation Reason': {
                            'Access Denied'
                        },
                        'Risk': 'Low',
                        'Savings': None,
                        'Source': 'Klera',
                        'Category': 'Cost Optimization'
                    }
                    recommendation.append(temp)
                continue
            for rule in res['ServerSideEncryptionConfiguration']['Rules']:
                if rule['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] == 'aws:kms' and rule['BucketKeyEnabled']:
                    temp = {
                        'Service Name': 'S3',
                        'Id': bucket['Name'],
                        'Recommendation': 'Enable s3 bucket keys',
                        'Description': 'Enable s3 bucket keys instead of KMS keys to optimize the aws cost',
                        'Metadata':{

                        },
                        'Recommendation Reason': {
                            # 'Average CPU Datapoints(7 days)': [float('{:.2f}'.format(x)) for x in tmp_lst_cpu]
                            'reason': 'KMS keys are used for encryption'
                        },
                        'Risk': 'Low',
                        'Savings': None,
                        'Source': 'Klera',
                        'Category': 'Cost Optimization'
                    }
                    recommendation.append(temp)

        return recommendation

    # Generate the recommendation for bucket versioning enabled
    def __s3_bucket_versioning_enabled(self, bucket_list: list):
        """
        :param bucket_list:
        :param self:
        :return dict: details of s3 bucket versioning enabled compliance.py
        """
        logger.info(" ---Inside s3 :: s3_bucket_versioning_enabled()")
        self.refresh_session()

        recommendation = []

        client = self.session.client('s3')

        for bucket in bucket_list:
            bucket_name = bucket['Name']

            try:
                resp = client.get_bucket_versioning(
                    Bucket=bucket_name,
                )
                status = resp['Status']
            except ClientError as e:
                if e.response['Error']['Code'] == 'AccessDenied':
                    logger.info('---------S3 read access denied----------')
                    temp = {
                        'Service Name': 'S3',
                        'Id': 'Access Denied',
                        'Recommendation': 'Access Denied',
                        'Description': 'Access Denied',
                        'Metadata': {
                            'Access Denied'
                        },
                        'Recommendation Reason': {
                            'Access Denied'
                        },
                        'Risk': 'Low',
                        'Savings': None,
                        'Source': 'Klera',
                        'Category': 'Operational Best Practice'
                    }
                    recommendation.append(temp)
                    return recommendation
                temp = {
                    'Service Name': 'S3',
                    'Id': bucket['Name'],
                    'Recommendation': 'Enable S3 bucket versioning',
                    'Description': 'Enable s3 bucket versioning',
                    'Metadata': {

                    },
                    'Recommendation Reason': {
                        'reason': 'Bucket versioning is not enabled'
                    },
                    'Risk': 'Low',
                    'Savings': None,
                    'Source': 'Klera',
                    'Category': 'Operational Best Practice'
                }
                recommendation.append(temp)
                continue
            except KeyError:
                temp = {
                    'Service Name': 'S3',
                    'Id': bucket['Name'],
                    'Recommendation': 'Enable S3 bucket versioning',
                    'Description': 'Enable s3 bucket versioning',
                    'Metadata': {

                    },
                    'Recommendation Reason': {
                        'reason': 'Bucket versioning is not enabled'
                    },
                    'Risk': 'Low',
                    'Savings': None,
                    'Source': 'Klera',
                    'Category': 'Operational Best Practice'
                }
                recommendation.append(temp)
                continue

            if not status == 'Enabled':
                temp = {
                    'Service Name': 'S3',
                    'Id': bucket['Name'],
                    'Recommendation': 'Enable S3 bucket versioning',
                    'Description': 'Enable s3 bucket versioning',
                    'Metadata': {

                    },
                    'Recommendation Reason': {
                        'reason': 'Bucket versioning is not enabled'
                    },
                    'Risk': 'Low',
                    'Savings': None,
                    'Source': 'Klera',
                    'Category': 'Operational Best Practice'
                }
                recommendation.append(temp)

        return recommendation

    #Generate the recommendation for s3 lifecycle enabled
    def __s3_bucket_lifecycle_configuration(self, bucket_list: list)-> list:
        """
        :param bucket_list:
        :param self:
        :return dict: details of s3 bucket versioning enabled compliance.py
        """
        logger.info(" ---Inside s3 :: s3_bucket_lifecycle_configuration()")
        self.refresh_session()

        recommendation = []

        client = self.session.client('s3')

        for bucket in bucket_list:
            bucket_name = bucket['Name']
            # print(bucket_name)
            try:
                resp = client.get_bucket_lifecycle_configuration(
                    Bucket=bucket_name,
                )
                # print(resp)
                flag = False
                for rule in resp['Rules']:
                    if rule['Status'] == 'Enabled':
                        flag = flag or True
                    else:
                        flag = flag or False

                if not flag:
                    temp = {
                        'Service Name': 'S3',
                        'Id': bucket['Name'],
                        'Recommendation': 'Add lifecycle rules to the bucket',
                        'Description': 'Add lifecycle rules to the bucket',
                        'Metadata': {

                        },
                        'Recommendation Reason': {
                            'reason': 'lifecycle rules are not there for s3 bucket'
                        },
                        'Risk': 'Low',
                        'Savings': None,
                        'Source': 'Klera',
                        'Category': 'Cost Optimization'
                    }
                    recommendation.append(temp)

            except ClientError as e:
                if e.response['Error']['Code'] == 'AccessDenied':
                    logger.info('---------S3 read access denied----------')
                    temp = {
                        'Service Name': 'S3',
                        'Id': 'Access Denied',
                        'Recommendation': 'Access Denied',
                        'Description': 'Access Denied',
                        'Metadata': {
                            # 'Exception': str(traceback.format_exc())
                        },
                        'Recommendation Reason': {
                            'Access Denied'
                        },
                        'Risk': 'Low',
                        'Savings': None,
                        'Source': 'Klera',
                        'Category': 'Cost Optimization'
                    }
                    recommendation.append(temp)
                    return recommendation
                temp = {
                    'Service Name': 'S3',
                    'Id': bucket['Name'],
                    'Recommendation': 'Add lifecycle rules to the bucket',
                    'Description': 'Add lifecycle rules to the bucket',
                    'Metadata': {

                    },
                    'Recommendation Reason': {
                        'reason': 'lifecycle rules are not there for s3 bucket'
                    },
                    'Risk': 'Low',
                    'Savings': None,
                    'Source': 'Klera',
                    'Category': 'Cost Optimization'
                }
                recommendation.append(temp)

        return recommendation
