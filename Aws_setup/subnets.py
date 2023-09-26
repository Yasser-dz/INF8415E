from typing import List
from boto3_type_annotations.ec2 import ServiceResource, Vpc, Subnet

def get_subnets(ec2: ServiceResource) -> Vpc:
    subnets: List[Subnet] = []
    for subnet in ec2.subnets.all():
        subnets.append(subnet)
    return subnets
