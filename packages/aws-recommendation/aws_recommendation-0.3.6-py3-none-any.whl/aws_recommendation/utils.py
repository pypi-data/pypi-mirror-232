import datetime as dt
import logging

from dateutil.relativedelta import relativedelta

r_logger = logging.getLogger('Recommender')
r_logger.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class utils:
    # returns the list of instances
    def list_instances(self, regions) -> dict:
        logger.info(" ---Inside utils :: list_instances()--- ")
        self.refresh_session()

        instance_lst = {}

        for region in regions:
            client = self.session.client('ec2', region_name=region)

            marker = ''
            while True:
                response = client.describe_instances(
                    MaxResults=1000,
                    NextToken=marker
                )
                for i in response['Reservations']:
                    for instance in i['Instances']:
                        state = instance['State']['Name']
                        if not state == 'terminated':
                            instance_lst.setdefault(region, []).append(instance)

                try:
                    marker = response['NextToken']
                    if marker == '':
                        break
                except KeyError:
                    break

        return instance_lst


    # returns the list of rds instances
    def list_rds_instances(self, regions) -> dict:
        """
        :param regions:
        :return:
        """
        logger.info(" ---Inside utils :: list_rds_instances()--- ")
        self.refresh_session()
        rds_instance_lst = {}

        for region in regions:
            client = self.session.client('rds', region_name=region)
            marker = ''
            while True:
                response = client.describe_db_instances(
                    MaxRecords=100,
                    Marker=marker
                )
                rds_instance_lst.setdefault(region, []).extend(response['DBInstances'])

                try:
                    marker = response['Marker']
                    if marker == '':
                        break
                except KeyError:
                    break
        return rds_instance_lst


    # returns the metrics data
    def get_metrics_stats(self, region, namespace: str, dimensions: list,
                          metric_name='CPUUtilization', start_time=dt.datetime.utcnow() - relativedelta(days=7),
                          end_time=dt.datetime.utcnow(), period=86400, stats=None, unit='Percent'):
        self.refresh_session()
        if stats is None:
            stats = ["Average"]

        client = self.session.client('cloudwatch', region_name=region)

        if unit is None:
            response_cpu = client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=stats,
                Dimensions=dimensions
            )
        else:
            response_cpu = client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=stats,
                Unit=unit,
                Dimensions=dimensions
            )
        return response_cpu


    # returns the list of redshift clusters
    def list_redshift_clusters(self, client) -> list:
        """
        :param client:
        :return:
        """
        logger.info(" ---Inside utils() :: list_redshift_clusters()")
        self.refresh_session()

        cluster_list = []

        marker = ''
        while True:
            if marker == '' or marker is None:
                response = client.describe_clusters()
            else:
                response = client.describe_clusters(
                    Marker = marker
                )
            cluster_list.extend(response['Clusters'])

            try:
                marker = response['Marker']
                if marker == '':
                    break
            except KeyError:
                break

        return cluster_list


    # returns the list of aws regions
    def get_regions(self):
        """
        :session: aws session object
        :return: list of regions
        """
        logger.info(" ---Inside utils :: get_regions()--- ")
        self.refresh_session()

        client = self.session.client('ec2', region_name='us-east-1')
        region_response = client.describe_regions()

        # regions = [region['RegionName'] for region in region_response['Regions']]

        # Create a list of region in which OptInStatus is equal to "opt-in-not-required"
        region_s = []
        for r in region_response['Regions']:
            if r['OptInStatus'] == 'opt-in-not-required':
                region_s.append(r['RegionName'])

        return region_s

#     returns the list of ebs volumes
    def list_ebs_volumes(self, regions: list) -> dict:
        """
        :param regions:
        :return:
        """
        logger.info("---Inside utils :: list_ebs_volumes()--- ")
        self.refresh_session()

        ebs_volumes = {}

        for region in regions:
            client = self.session.client('ec2', region_name=region)
            marker = ''
            while True:
                response = client.describe_volumes(
                    Filters=[
                        {
                            'Name': 'status',
                            'Values': [
                                'in-use'
                            ]
                        },
                    ],
                    MaxResults=500,
                    NextToken=marker
                )
                ebs_volumes.setdefault(region, []).extend(response['Volumes'])
                try:
                    marker = response['NextToken']
                    if marker == '':
                        break
                except KeyError:
                    break

        return ebs_volumes
