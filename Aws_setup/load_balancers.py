import logging, sys
from time import sleep
from typing import List, Any
from boto3_type_annotations.elbv2 import Client
from boto3_type_annotations.ec2 import Vpc, SecurityGroup, Subnet, Instance

def delete_all_target_groups(client: Client):
    logging.info('Deleting all target groups...')
    target_groups = client.describe_target_groups()['TargetGroups']
    for target_group in target_groups:
        success=False
        for i in range(10):
            try:
                client.delete_target_group(TargetGroupArn=target_group['TargetGroupArn'])
                logging.info('  {}: Deleted.'.format(target_group['TargetGroupName']))
                success=True
                break
            except:
                sleep(5)
        if not success:
            logging.error('Unable to delete the target group.')
            sys.exit(1)
        

def get_target_group(client: Client, name: str):
    target_groups = client.describe_target_groups()['TargetGroups']
    for target_group in target_groups:
        if target_group['TargetGroupName'] == name:
            return target_group

def create_target_group(client: Client, name: str, vpc: Vpc, instances: List[Instance]):
    logging.info(f'Creating the target group "{name}"...')
    target_group = client.create_target_group(
        Name=name, 
        Protocol='HTTP',
        Port=80,
        HealthCheckProtocol='HTTP',
        HealthCheckEnabled=True,
        HealthCheckPath='/ping',
        TargetType='instance',
        IpAddressType='ipv4',
        VpcId=vpc.id
    )['TargetGroups'][0]

    targets = []
    for instance in instances:
        targets.append({
            'Id': instance.id,
            'Port': 80
        })

    client.register_targets(
        TargetGroupArn=target_group['TargetGroupArn'],
        Targets=targets
    )

    return target_group


def delete_load_balancers(client: Client):
    logging.info('Deleting all load balancers...')
    load_balancers = client.describe_load_balancers()['LoadBalancers']
    for load_balancer in load_balancers:
        client.delete_load_balancer(LoadBalancerArn=load_balancer['LoadBalancerArn'])
        logging.info('  {}: Deleted.'.format(load_balancer['LoadBalancerName']))
    


def create_load_balancer(client: Client, name: str, security_group: SecurityGroup, subnets: List[Subnet], cluster1: Any, cluster2: Any):
    # Retrieve subnet ids
    subnet_ids = []
    for subnet in subnets:
        subnet_ids.append(subnet.id)

    # Create the load balancer
    logging.info(f'Creating the load balancer "{name}"...')
    load_balancer = client.create_load_balancer(
        Name=name,
        SecurityGroups=[security_group.group_id],
        Type='application',
        Scheme='internet-facing',
        IpAddressType='ipv4',
        Subnets=subnet_ids,
    )['LoadBalancers'][0]

    # Add the listener
    logging.info('Creating a listener for HTTP port 80...')
    listener = client.create_listener(
        LoadBalancerArn=load_balancer['LoadBalancerArn'],
        Protocol='HTTP',
        Port=80,
        DefaultActions=[
            {
                'Type': 'fixed-response',
                'FixedResponseConfig': {
                    'MessageBody': 'This route is not available.',
                    'StatusCode': '404'
                }
            }
        ]
    )['Listeners'][0]

    # Add the cluster 1 rule
    logging.info('Creating a rule for /cluster1...')
    rule1 = client.create_rule(
        ListenerArn=listener['ListenerArn'],
        Priority=2,
        Conditions=[
            {
                'Field': 'path-pattern',
                'Values': [
                    '/cluster1',
                ]
            },
        ],
        Actions=[
            {
                'Type': 'forward',
                'ForwardConfig': {
                    'TargetGroups': [
                        {
                            'TargetGroupArn': cluster1['TargetGroupArn'],
                            'Weight': 1
                        },
                    ]
                }
            },
        ]
    )['Rules'][0]

    # Add the cluster 2 rule
    logging.info('Creating a rule for /cluster2...')
    rule2 = client.create_rule(
        ListenerArn=listener['ListenerArn'],
        Priority=3,
        Conditions=[
            {
                'Field': 'path-pattern',
                'Values': [
                    '/cluster2',
                ]
            },
        ],
        Actions=[
            {
                'Type': 'forward',
                'ForwardConfig': {
                    'TargetGroups': [
                        {
                            'TargetGroupArn': cluster2['TargetGroupArn'],
                            'Weight': 1
                        },
                    ]
                }
            },
        ]
    )['Rules'][0]

    return load_balancer

def wait_for_provisioning(client: Client, load_balancer: Any):
    logging.info('Waiting for provisioning...')
    while True:
        load_balancers = client.describe_load_balancers()['LoadBalancers']
        for load_balancer_info in load_balancers:
            if load_balancer_info['LoadBalancerArn'] == load_balancer['LoadBalancerArn']:
                if load_balancer_info['State']['Code'] == 'active':
                    return load_balancer_info
                sleep(2)

def get_load_balancer(client: Client, name: str):
    load_balancers = client.describe_load_balancers()['LoadBalancers']
    for load_balancer in load_balancers:
        if load_balancer['LoadBalancerName'] == name:
            return load_balancer

def wait_for_healthy_target(client: Client, target_group: Any):
    logging.info('Waiting for all instances of target group "{}" to be healthy...'.format(target_group['TargetGroupName']))
    
    targets = None
    while True:
        health = client.describe_target_health(
            TargetGroupArn=target_group['TargetGroupArn']
        )
        if targets is None:
            targets = {}
            for target in health['TargetHealthDescriptions']:
                targets[target['Target']['Id']] = False
        all_healty = True
        for target in health['TargetHealthDescriptions']:
            if target['TargetHealth']['State'] == 'healthy':
                if not targets[target['Target']['Id']]:
                    logging.info('  {}: Healthy.'.format(target['Target']['Id']))
                    targets[target['Target']['Id']] = True
            if target['TargetHealth']['State'] != 'healthy':
                all_healty = False
        if all_healty:
            return