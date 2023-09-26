from botocore.exceptions import ClientError

from aws_recommendation.utils import *


class dynamodb:
    def get_dynamodb_recommendations(self, regions=None):
        """
        :param regions:
        :return:
        """
        logger.info(" ---Inside dynamodb :: get_dynamodb_recommendations()--- ")

        if regions is None:
            regions = self.get_regions()

        return self.unused_dynamodb_tables(regions)

    # generated the recommendations for unused dynamodb tables
    def unused_dynamodb_tables(self, regions) -> list:
        """
        :param regions:
        :param self:
        :return:
        """
        self.refresh_session()
        logger.info(" ---Inside dynamodb :: unused_dynamodb_tables()")

        recommendation = []

        for region in regions:
            try:
                client = self.session.client('dynamodb', region_name=region)

                marker=''
                while True:
                    if marker == '':
                        response = client.list_tables()
                    else:
                        response = client.list_tables(
                            ExclusiveStartTableName=marker
                        )
                    for table in response['TableNames']:
                        table_desc = client.describe_table(
                            TableName=table
                        )
                        if table_desc['Table']['ItemCount'] == 0:
                            temp = {
                                'Service Name': 'DynamoDB',
                                'Id': table,
                                'Recommendation': 'Remove Dynamodb table',
                                'Description': 'Identify any unused Amazon DynamoDB tables available within your AWS account and remove them to help lower the cost of your monthly AWS bill. A DynamoDB table is considered unused if it’s ItemCount parameter, which describes the number of items in the table, is equal to 0 (zero)',
                                'Metadata': {
                                    'Region': region,
                                    'TableStatus': table_desc['Table']['TableStatus']
                                },
                                'Recommendation Reason': {
                                    'reason': "The ItemCount parameter value is 0, therefore the selected amazon dynamodb table is not currently in use and can be safely removed from your AWS Account"
                                },
                                'Risk': 'Medium',
                                'Savings': None,
                                'Source': 'Klera',
                                'Category': 'Cost Optimization'
                            }
                            recommendation.append(temp)
                    try:
                        marker = response['LastEvaluatedTableName']
                        if marker == '':
                            break
                    except KeyError:
                        break
            except ClientError as e:
                if e.response['Error']['Code'] == 'AccessDenied' or e.response['Error']['Code'] == 'AccessDeniedException':
                    logger.warning(e)
                    logger.info('---------Dynamodb read access denied----------')
                    temp = {
                        'Service Name': 'DynamoDB',
                        'Id': 'Access Denied',
                        'Recommendation': 'Access Denied',
                        'Description': 'Access Denied',
                        'Metadata': {
                            'Access Denied'
                        },
                        'Recommendation Reason': {
                            'Access Denied'
                        },
                        'Risk': 'Medium',
                        'Savings': None,
                        'Source': 'Klera',
                        'Category': 'Cost Optimization'
                    }
                    recommendation.append(temp)
                    return recommendation
                logger.warning("Something went wrong with the region {}: {}".format(region, e))

        return recommendation