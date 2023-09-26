from botocore.exceptions import ClientError

from aws_recommendation.utils import *


class ebs:
    def get_ebs_recommendations(self, regions=None, ebs_volumes=None)-> list:
        """
        :param regions:
        :param ebs_volumes:
        :return:
        """
        logger.info(" ---Inside ebs :: get_ebs_recommendations()--- ")

        if regions is None:
            regions = self.get_regions()
        if ebs_volumes is None:
            ebs_volumes = self.list_ebs_volumes(regions)

        return self.idle_ebs_volumes(ebs_volumes) + self.ebs_general_purpose_ssd(ebs_volumes) + \
            self.unused_ebs_volume(ebs_volumes) + self.gp2_to_gp3(ebs_volumes)

    # Generated the recommendation for unused EBS volumes
    def idle_ebs_volumes(self, ebs_volumes) -> list:
        """
        :param ebs_volumes:
        :param self:
        :return:
        """
        self.refresh_session()
        logger.info(" ---Inside ebs :: idle_ebs_volumes")

        recommendation = []

        try:
            for region, volumes in ebs_volumes.items():
                for volume in volumes:
                    # device = volume['Attachments']['Device']
                    if '/dev/xvda' not in [x['Device'] for x in volume['Attachments']]:
                        read_datapoints = self.get_metrics_stats(
                            region=region,
                            namespace='AWS/EBS',
                            dimensions= [
                                {
                                    'Name':'VolumeId',
                                    'Value': volume['VolumeId']
                                }
                            ],
                            metric_name='VolumeReadOps',
                            period=3600,
                            stats=['Sum']
                        )
                        sum_read_ops = 0
                        for datapoint in read_datapoints['Datapoints']:
                            print(type(datapoint))
                            print(datapoint)
                            sum_read_ops = sum_read_ops + datapoint['Sum']

                        flag = True

                        if sum_read_ops > 1:
                            flag = False

                        if flag:
                            write_datapoints = self.get_metrics_stats(
                                region=region,
                                namespace='AWS/EBS',
                                dimensions=[
                                    {
                                        'Name': 'VolumeId',
                                        'Value': volume['VolumeId']
                                    }
                                ],
                                metric_name='VolumeReadOps',
                                period=3600,
                                stats=['Sum']
                            )
                            write_sum = 0
                            for datapoint in write_datapoints['Datapoints']:
                                write_sum = write_sum + datapoint['Sum']

                            if write_sum > 1:
                                flag = False

                        if flag:
                            try:
                                tags = volume['Tags']
                            except KeyError:
                                tags = None

                            recommend_flag = True
                            try:
                                for tag in tags:
                                    if 'Role' in tag['Key']:
                                        recommend_flag = False
                            except TypeError:
                                pass
                            if recommend_flag:
                                temp = {
                                    'Service Name': 'EC2 (EBS)',
                                    'Id': volume['VolumeId'],
                                    'Recommendation': 'Delete idle EBS volume',
                                    'Description': 'The selected EBS volume is considered "idle" and can be safely removed from the AWS account to reduce the EBS monthly costs.',
                                    'Metadata': {
                                        'Region': region,
                                        'Instance Type': volume['VolumeType'],
                                        'Tags': tags,
                                        'CreateTime': volume['CreateTime']
                                    },
                                    'Recommendation Reason': {
                                        'reason': "Volume is idle"
                                    },
                                    'Risk': 'Medium',
                                    'Savings': None,
                                    'Source': 'Klera',
                                    'Category': 'Cost Optimization'
                                }
                                recommendation.append(temp)

        except ClientError as e:
            if e.response['Error']['Code'] == 'UnauthorizedOperation':
                logger.info('---------EBS read access denied----------')
                temp = {
                    'Service Name': 'EC2 (EBS)',
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


    # Generated the recommendation for general purpose ssd
    def ebs_general_purpose_ssd(self, ebs_volumes) -> list:
        """
        :param ebs_volumes:
        :param self:
        :return:
        """
        self.refresh_session()
        logger.info(" ---Inside ebs :: ebs_general_purpose_ssd()")

        recommendation = []

        try:
            for region, volumes in ebs_volumes.items():
                for volume in volumes:
                    storage_type = volume['VolumeType']
                    if storage_type == 'io1' or storage_type == 'io2':
                        try:
                            tags = volume['Tags']
                        except KeyError:
                            tags = None

                        temp = {
                            'Service Name': 'EC2 (EBS)',
                            'Id': volume['VolumeId'],
                            'Recommendation': 'Upgrade Storage Type',
                            'Description': 'Ensure that your Amazon EC2 instances are using General Purpose SSD volumes instead of Provisioned IOPS SSD volumes for cost-effective storage that fits a broad range of workloads',
                            'Metadata': {
                                'Region': region,
                                'Instance Type': volume['VolumeType'],
                                'Tags': tags,
                                'CreateTime': volume['CreateTime'],
                                'size': volume['Size']
                            },
                            'Recommendation Reason': {
                                'reason': "the storage type configured for the selected Amazon EBS volume is Provisioned IOPS (PIOPS) SSD, therefore the verified EBS volume is not optimized with respect to cost."
                            },
                            'Risk': 'Medium',
                            'Savings': None,
                            'Source': 'Klera',
                            'Category': 'Cost Optimization'
                        }
                        recommendation.append(temp)

        except ClientError as e:
            if e.response['Error']['Code'] == 'UnauthorizedOperation':
                logger.info('---------EBS read access denied----------')
                temp = {
                    'Service Name': 'EC2 (EBS)',
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


    # Generate the recommendation for upgrade volume from GP2 to gp3 to save cost
    def gp2_to_gp3(self, ebs_volumes) -> list:
        """
        :param ebs_volumes:
        :param self:
        :return:
        """
        self.refresh_session()
        logger.info(" ---Inside ebs :: gp2_to_gp3()")

        recommendation = []

        try:
            for region, volumes in ebs_volumes.items():
                for volume in volumes:
                    storage_type = volume['VolumeType']
                    if storage_type == 'gp2':
                        try:
                            tags = volume['Tags']
                        except KeyError:
                            tags = None

                        size = volume['Size']
                        cost = size * 0.10
                        savings = cost * 20 /100
                        temp = {
                            'Service Name': 'EC2 (EBS)',
                            'Id': volume['VolumeId'],
                            'Recommendation': 'Migrate GP2 volume to GP3',
                            'Description': 'gp3 offers SSD-performance at a 20% lower cost per GB than gp2 volumes',
                            'Metadata': {
                                'Region': region,
                                'Instance Type': volume['VolumeType'],
                                'Tags': tags,
                                'CreateTime': volume['CreateTime']
                            },
                            'Recommendation Reason': {
                                'reason': "the storage type configured for the selected Amazon EBS volume is GP2, it can be migrated to GP3 to save AWS costs."
                            },
                            'Risk': 'High',
                            'Savings': str(savings),
                            'Source': 'Klera',
                            'Category': 'Cost Optimization'
                        }
                        recommendation.append(temp)

        except ClientError as e:
            if e.response['Error']['Code'] == 'UnauthorizedOperation':
                logger.info('---------EBS read access denied----------')
                temp = {
                    'Service Name': 'EC2 (EBS)',
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
                    'Savings': 'None',
                    'Source': 'Klera',
                    'Category': 'Cost Optimization'
                }
                recommendation.append(temp)
                return recommendation
            logger.warning("Something went wrong with the region {}: {}".format(region, e))

        return recommendation


    # Generate recommendation for unused ebs volume
    def unused_ebs_volume(self, ebs_volumes) -> list:
        """
        :param ebs_volumes:
        :param self:
        :return:
        """
        self.refresh_session()
        logger.info(" ---Inside ebs :: unused_ebs_volume()")

        recommendation = []

        try:
            for region, volumes in ebs_volumes.items():
                for volume in volumes:
                    state = volume['State']
                    if state == 'available':
                        try:
                            tags = volume['Tags']
                        except KeyError:
                            tags = None

                        temp = {
                            'Service Name': 'EC2 (EBS)',
                            'Id': volume['VolumeId'],
                            'Recommendation': 'Remove unused EBS volume',
                            'Description': 'Amazon EBS volume is not attached to any EC2 instance. Remove it to save aws costs',
                            'Metadata': {
                                'Region': region,
                                'Instance Type': volume['VolumeType'],
                                'Tags': tags,
                                'CreateTime': volume['CreateTime']
                            },
                            'Recommendation Reason': {
                                'reason': "Amazon EBS volume is not attached to any EC2 instance. "
                            },
                            'Risk': 'Medium',
                            'Savings': '100%',
                            'Source': 'Klera',
                            'Category': 'Cost Optimization'
                        }
                        recommendation.append(temp)

        except ClientError as e:
            if e.response['Error']['Code'] == 'UnauthorizedOperation':
                logger.info('---------EBS read access denied----------')
                temp = {
                    'Service Name': 'EC2 (EBS)',
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