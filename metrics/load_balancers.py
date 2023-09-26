import logging, boto3, sys
from typing import List, Any
from boto3_type_annotations.elbv2 import Client
from boto3_type_annotations.ec2 import Vpc, SecurityGroup, Subnet, Instance

CLIENT: Client = boto3.client('elbv2')

def get_load_balancer(name: str):
    logging.info(f'Retrieving load balancer "{name}"...')
    load_balancers = CLIENT.describe_load_balancers()['LoadBalancers']
    for load_balancer in load_balancers:
        if load_balancer['LoadBalancerName'] == name:
            return load_balancer
    logging.error(f'Unable to retrieve load balancer "{name}".')
    sys.exit(1)

def get_target_group(name: str):
    logging.info(f'Retrieving target group "{name}"...')
    target_groups = CLIENT.describe_target_groups()['TargetGroups']
    for target_group in target_groups:
        if target_group['TargetGroupName'] == name:
            return target_group
    logging.error(f'Unable to retrieve target group "{name}".')
    sys.exit(1)
