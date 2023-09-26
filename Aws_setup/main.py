
from time import sleep
from typing import List
import boto3
import logging
from boto3_type_annotations.elbv2 import Client as elbv2Client
from boto3_type_annotations.ec2 import ServiceResource as ec2ServiceResource
from boto3_type_annotations.ec2 import Instance
import security_groups, instances, load_balancers, vpcs, subnets

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

SECURITY_GROUP_NAME = 'tp1'
INSTANCE_INFOS = [
    {'type': 't2.large', 'zone': 'us-east-1a'},
    {'type': 't2.large', 'zone': 'us-east-1b'},
    {'type': 't2.large', 'zone': 'us-east-1c'},
    {'type': 't2.large', 'zone': 'us-east-1d'},
    {'type': 't2.large', 'zone': 'us-east-1e'},
    {'type': 'm4.large', 'zone': 'us-east-1f'},
    {'type': 'm4.large', 'zone': 'us-east-1a'},
    {'type': 'm4.large', 'zone': 'us-east-1b'},
    {'type': 'm4.large', 'zone': 'us-east-1c'}
]

ec2: ec2ServiceResource = boto3.resource('ec2')

elbv2: elbv2Client = boto3.client('elbv2')

# Retrieve default Vpc
vpc = vpcs.get_default_vpc(ec2)

# Retrieve subnets
subnets_list = subnets.get_subnets(ec2)

# Delete all old objects
instances.delete_all_instances(ec2)
load_balancers.delete_load_balancers(elbv2)
load_balancers.delete_all_target_groups(elbv2)
security_groups.delete_security_group(ec2, SECURITY_GROUP_NAME)

# Create the security group
security_group = security_groups.create_security_group(ec2, SECURITY_GROUP_NAME)
security_group = security_groups.get_security_group(ec2, 'tp1')

# Create an instance
initialized_instances: List[Instance] = []
for instance_info in INSTANCE_INFOS:
    initialized_instances.append(instances.create_instance(ec2, instance_info['type'], instance_info['zone'], security_group))

# Wait for instances to be running
instances.wait_for_running(initialized_instances)

# Retrieve instances
cluster1_instances = instances.retreive_instances(ec2, 't2.large')
cluster2_instances = instances.retreive_instances(ec2, 'm4.large')

# Create load balancer
target_group_1 = load_balancers.create_target_group(elbv2, 'cluster1', vpc, cluster1_instances)
target_group_2 = load_balancers.create_target_group(elbv2, 'cluster2', vpc, cluster2_instances)
target_group_1 = load_balancers.get_target_group(elbv2, 'cluster1')
target_group_2 = load_balancers.get_target_group(elbv2, 'cluster2')
load_balancer = load_balancers.create_load_balancer(elbv2, 'tp1', security_group, subnets_list, target_group_1, target_group_2)
load_balancer = load_balancers.get_load_balancer(elbv2, 'tp1')
load_balancer = load_balancers.wait_for_provisioning(elbv2, load_balancer)

# Wait for all targets to be healty
load_balancers.wait_for_healthy_target(elbv2, target_group_1)
load_balancers.wait_for_healthy_target(elbv2, target_group_2)

# Retrieving urls
dns_name = load_balancer['DNSName']
base_url = f'http://{dns_name}'
cluster1_url = base_url + '/cluster1'
cluster2_url = base_url + '/cluster2'
logging.info('URLs:')
logging.info('  ' + cluster1_url)
logging.info('  ' + cluster2_url)

exit(0)


