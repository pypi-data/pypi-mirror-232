import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


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


def list_volumes(self, regions: list) -> dict:
    """
    :param regions:
    :param session:
    :return:
    """
    logger.info(" ---Inside utils :: list_gp2_volumes()--- ")
    self.refresh_session()

    volume_list = {}

    for region in regions:
        client = self.session.client('ec2', region_name=region)
        marker = ''
        while True:
            if marker == '':
                response = client.describe_volumes()
            else:
                response = client.describe_volumes(
                    NextToken=marker
                )
            volume_list.setdefault(region, []).extend(response['Volumes'])

            try:
                marker = response['NextToken']
                if marker == '':
                    break
            except KeyError:
                break

    return volume_list


# returns the pricing of resource
def get_pricing(self, region: str, service_code: str, Filters: list, service_name: str) -> dict:
    """
    :param self:
    :param service_name:
    :param Filters:
    :param service_code:
    :param region: aws region
    :param session: aws session
    :return: pricing
    """
    logger.info(" ---Inside utils :: get_pricing()--- ")
    self.refresh_session()

    aws_pricing_region = region

    client = self.session.client('pricing', 'us-east-1')

    response = client.get_products(
        ServiceCode=service_code,
        Filters=Filters
    )
    print(response)
    prices = {}
    for price in response['PriceList']:
        price = json.loads(price)
        # print(json.dumps(price, indent=4))
        for key in price['terms']['OnDemand'].keys():
            for k in price['terms']['OnDemand'][key]['priceDimensions'].keys():
                temp = price['terms']['OnDemand'][key]['priceDimensions'][k]['pricePerUnit']['USD']

                if service_name == 'volume':
                    prices[price['product']['attributes']['volumeApiName']] = temp
                elif service_name == 'rds' or service_name == 'ec2_instance':
                    prices[price['product']['attributes']['instanceType']] = temp
                elif service_name == 'eip':
                    if price['terms']['OnDemand'][key]['priceDimensions'][k]['endRange'] == 'Inf':
                        prices[price['product']['attributes']['usagetype']] = temp
                elif service_name == 'snapshot':
                    prices[price['product']['attributes']['usagetype']] = temp
                elif service_name == 'rds_storage':
                    prices[price['product']['attributes']['volumeName']] = temp
                elif service_name == 'cmk':
                    prices[price['product']['attributes']['servicename']] = temp
                elif service_name == 'cwlog':
                    prices[price['product']['attributes']['servicename']] = temp
                elif service_name == 'elb':
                    prices[price['product']['attributes']['groupDescription']] = temp

    return prices


# returns the list of rds instances
def list_rds_instances(self, regions: list) -> dict:
    """
    :param self:
    :param regions:
    :param session:
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


# returns the list of ec2 instances
def list_ec2_instances(self, regions: list) -> dict:
    """
    :param self:
    :param regions:
    :return:
    """
    logger.info(" ---Inside utils :: list_ec2_instances()--- ")
    self.refresh_session()

    instances = {}
    print('Instances')
    for region in regions:
        client = self.session.client('ec2', region_name=region)
        marker = ''
        while True:
            if marker == '':
                response = client.describe_instances()
            else:
                response = client.describe_instances(
                    NextToken=marker
                )
            instances.setdefault(region, []).extend(response['Reservations'])
            print(response)

            try:
                marker = response['NextToken']
                if marker == '':
                    break
            except KeyError:
                break

    return instances


# returns the list eip
def list_eip(self, regions: list) -> dict:
    """
    :param self:
    :param regions:
    :return:
    """
    logger.info(" ---Inside utils :: list_eip()--- ")
    self.refresh_session()

    eip_list = {}

    for region in regions:
        client = self.session.client('ec2', region_name=region)
        response = client.describe_addresses()
        eip_list.setdefault(region, []).extend(response['Addresses'])

    return eip_list
