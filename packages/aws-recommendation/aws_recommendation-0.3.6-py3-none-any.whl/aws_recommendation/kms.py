from botocore.exceptions import ClientError

from aws_recommendation.utils import *

class kms:
    def get_kms_recommendations(self, regions=None):
        """
        :param regions:
        :return:
        """
        logger.info(" ---Inside kms :: get_kms_recommendations()--- ")

        if regions is None:
            regions = self.get_regions()

        return self.unused_cmk(regions)

    # generate the recommendations for unused cmk
    def unused_cmk(self, regions: list) -> list:
        """
        :param regions:
        :param self:
        :return:
        """
        logger.info(" ---Inside kms :: unused_cmk()")
        self.refresh_session()

        recommendation = []

        for region in regions:
            try:
                client = self.session.client('kms', region_name=region)

                marker = ''
                while True:
                    if marker == '':
                        response = client.list_keys(
                            Limit=1000
                        )
                    else:
                        response = client.list_keys(
                            Limit=1000,
                            Marker=marker
                        )
                    for key in response['Keys']:
                        key_desc = client.describe_key(
                            KeyId=key['KeyId']
                        )
                        if not key_desc['KeyMetadata']['Enabled']:
                            temp = {
                                'Service Name': 'Key Management Service',
                                'Id': key['KeyId'],
                                'Recommendation': 'Remove Customer Master Key',
                                'Description': 'Check for any disabled KMS Customer Master Keys in your AWS account and remove them in order to lower the cost of your monthly AWS bill',
                                'Metadata': {
                                    'Region': region,
                                    'CreationDate': key_desc['KeyMetadata']['CreationDate'],
                                    'Enabled': key_desc['KeyMetadata']['Enabled'],
                                    'MultiRegion': key_desc['KeyMetadata']['MultiRegion']
                                },
                                'Recommendation Reason': {
                                    'reason': "Customer Master key is not in enabled state"
                                },
                                'Risk': 'Low',
                                'Savings': None,
                                'Source': 'Klera',
                                'Category': 'Cost Optimization'
                            }
                            recommendation.append(temp)
                    try:
                        marker = response['NextMarker']
                        if marker == '':
                            break
                    except KeyError:
                        break
            except ClientError as e:
                if e.response['Error']['Code'] == 'AccessDenied' or e.response['Error']['Code'] == 'AccessDeniedException':
                    logger.info('---------KMS read access denied----------')
                    temp = {
                        'Service Name': 'Key Management Service',
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
                        'Category': 'Cost Optimization'
                    }
                    recommendation.append(temp)
                    return recommendation
                logger.warning("Something went wrong with the region {}: {}".format(region, e))

        return recommendation
