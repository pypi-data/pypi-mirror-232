import logging

import botocore
from botocore.exceptions import ClientError

from aws_recommendation import utils
from aws_recommendation.utils import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class rds:
    def get_rds_recommendations(self, regions):
        """
        :return:
        """
        logger.info(" ---Inside rds :: get_rds_recommendations()--- ")

        rds_instances = self.list_rds_instances(regions)
        response = []
        # r_logger.debug(str(rds_instances))

        response.extend(self.downsize_underutilized_rds_recommendation(rds_instances))
        response.extend(self.rds_idle_db_instances(rds_instances))
        response.extend(self.rds_general_purpose_ssd(rds_instances))

        return response

    # Generates the recommendation to downsize underutilized rds instance
    def downsize_underutilized_rds_recommendation(self, rds_instances) -> list:
        logger.info(" ---Inside downsize_underutilized_rds_recommendation()")
        self.refresh_session()

        recommendation = []

        try:
            for region, instances in rds_instances.items():
                for instance in instances:
                    cpu_stats = self.get_metrics_stats(
                        region, namespace='AWS/RDS',
                        dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': instance['DBInstanceIdentifier']}]
                    )

                    if len(cpu_stats['Datapoints']) >= 7:
                        flag = True
                        for points in cpu_stats['Datapoints']:
                            if points['Average'] > 30:
                                flag = False
                                break

                        if flag:
                            try:
                                Tags = instance['TagList']
                            except KeyError:
                                Tags = None
                            temp = {
                                'Service Name': 'RDS',
                                'Id': instance['DBInstanceIdentifier'],
                                'Recommendation': 'Downsize underutilized rds instance',
                                'Description': 'The Downsize underutilized rds databases recommendation indicates that more CPUs are allocated to autonomous databases than you need. Reducing the number of CPUs allocated to your databases saves you money.',
                                'Metadata': {
                                    'Region': region,
                                    'DBInstanceClass': instance['DBInstanceClass'],
                                    'MultiAZ': instance['MultiAZ'],
                                    'Engine': instance['Engine'],
                                    'Tags': Tags,
                                    'InstanceCreateTime': instance['InstanceCreateTime']
                                },
                                'Recommendation Reason': {
                                    'Average CPU Datapoints(7 days)': [float('{:.2f}'.format(item['Average'])) for item in cpu_stats['Datapoints']]
                                },
                                'Risk': 'High',
                                'Savings': None,
                                'Source': 'Klera',
                                'Category': 'Cost Optimization'
                            }
                            recommendation.append(temp)

        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied' or e.response['Error']['Code'] == 'AccessDeniedException':
                logger.info('---------RDS read access denied----------')
                temp = {
                    'Service Name': 'RDS',
                    'Id': 'Access Denied',
                    'Recommendation': 'Access Denied',
                    'Description': 'Access Denied',
                    'Metadata': {
                        'Access Denied'
                    },
                    'Recommendation Reason': {
                        'Access Denied'
                    },
                    'Risk': 'High',
                    'Savings': None,
                    'Source': 'Klera',
                    'Category': 'Cost Optimization'
                }
                recommendation.append(temp)
                return recommendation
            logger.info("Something wrong with the region {}: {}".format(region, e))

        return recommendation


    # Generates the recommendation Amazon RDS Idle DB Instances
    def rds_idle_db_instances(self, rds_instances) -> list:
        """

        :param self:
        :return list: recommendation list for rds idle db instances
        """
        logger.info(' ---Inside rds :: rds_idle_db_instances()')
        self.refresh_session()

        recommendation = []

        try:
            for region, instances in rds_instances.items():
                for instance in instances:
                    datapoints = self.get_metrics_stats(
                        region, namespace='AWS/RDS',
                        dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': instance['DBInstanceIdentifier']}], metric_name='DatabaseConnections', stats=['Maximum'], unit='Count'
                    )
                    flag = True
                    for points in datapoints['Datapoints']:
                        if points['Maximum'] > 0:
                            flag = False
                            break

                    if flag:
                        try:
                            Tags = instance['TagList']
                        except KeyError:
                            Tags = None
                        temp = {
                            'Service Name': 'RDS',
                            'Id': instance['DBInstanceIdentifier'],
                            'Recommendation': 'Delete idle rds instance',
                            'Description': 'Consider taking a snapshot of the idle DB instance and then either stopping it or deleting it. Stopping the DB instance removes some of the costs for it, but does not remove storage costs. A stopped instance keeps all automated backups based upon the configured retention period. Stopping a DB instance usually incurs additional costs when compared to deleting the instance and then retaining only the final snapshot',
                            'Metadata': {
                                'Region': region,
                                'DBInstanceClass': instance['DBInstanceClass'],
                                'MultiAZ': instance['MultiAZ'],
                                'Engine': instance['Engine'],
                                'Tags': Tags,
                                'InstanceCreateTime': instance['InstanceCreateTime']
                            },
                            'Recommendation Reason': {
                                'Reason': 'An active DB instance has not had a connection in the last 7 days.'
                            },
                            'Risk': 'High',
                            'Savings': None,
                            'Source': 'Klera',
                            'Category': 'Cost Optimization'
                        }
                        recommendation.append(temp)

        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied' or e.response['Error']['Code'] == 'AccessDeniedException':
                logger.info('---------RDS read access denied----------')
                temp = {
                    'Service Name': 'RDS',
                    'Id': 'Access Denied',
                    'Recommendation': 'Access Denied',
                    'Description': 'Access Denied',
                    'Metadata': {
                        'Access Denied'
                    },
                    'Recommendation Reason': {
                        'Access Denied'
                    },
                    'Risk': 'High',
                    'Savings': None,
                    'Source': 'Klera',
                    'Category': 'Cost Optimization'
                }
                recommendation.append(temp)
                return recommendation
            logger.info("Something wrong with the region {}: {}".format(region, e))

        return recommendation


    #Generated the recommendation for rds general purpose ssd
    def rds_general_purpose_ssd(self, rds_instances) -> list:
        """
        :param rds_instances:
        :param self:
        :return:
        """
        logger.info(' ---Inside rds :: rds_general_purpose_ssd()')
        self.refresh_session()

        recommendation = []

        try:
            for region, instances in rds_instances.items():
                for instance in instances:
                    storage = instance['StorageType']
                    if storage == 'io1':
                        try:
                            Tags = instance['TagList']
                        except KeyError:
                            Tags = None
                        temp = {
                            'Service Name': 'RDS',
                            'Id': instance['DBInstanceIdentifier'],
                            'Recommendation': 'Upgrade to General Purpose SSD',
                            'Description': 'Using General Purpose (GP) SSD database storage instead of Provisioned IOPS (PIOPS) SSD storage represents a good strategy to cut down on AWS RDS costs because for GP SSDs you only pay for the storage compared to PIOPS SSDs where you pay for both storage and IOPS',
                            'Metadata': {
                                'Region': region,
                                'DBInstanceClass': instance['DBInstanceClass'],
                                'Engine': instance['Engine'],
                                'Tags': Tags,
                                'InstanceCreateTime': instance['InstanceCreateTime']
                            },
                            'Recommendation Reason': {
                                'Reason': 'the storage type used is Provisioned IOPS SSD'
                            },
                            'Risk': 'Medium',
                            'Savings': None,
                            'Source': 'Klera',
                            'Category': 'Cost Optimization'
                        }
                        recommendation.append(temp)
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied' or e.response['Error']['Code'] == 'AccessDeniedException':
                logger.info('---------RDS read access denied----------')
                temp = {
                    'Service Name': 'RDS',
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
            logger.info("Something went wrong with the region {}: {}".format(region, e))

        return recommendation
