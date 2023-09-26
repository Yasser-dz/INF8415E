import logging, boto3, sys, json
from typing import List
from boto3_type_annotations.cloudwatch import Client
from datetime import datetime, timedelta

NOW        = datetime.utcnow()
NOW        = datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute)
END_TIME   = NOW + timedelta(minutes=2)
START_TIME = END_TIME - timedelta(minutes=10)
PERIOD = 60
PERIOD_TD = timedelta(seconds=PERIOD)

CLIENT: Client = boto3.client('cloudwatch')

def get_elb_metric_data(load_balancer, metric_name: str, stat: str, unit: str):

    # Hack for milliseconds
    is_ms = unit == 'Milliseconds'
    if is_ms: 
        unit = 'Seconds'

    tmp=load_balancer['LoadBalancerArn'].split(':')[-1].split('/')
    lbstring=tmp[1]+'/'+tmp[2]+'/'+tmp[3]

    logging.info(f'Getting metric "{metric_name}" for load balancer "{lbstring}"')

    response = CLIENT.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'string',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': metric_name,
                        'Dimensions': [
                            {
                                'Name': 'LoadBalancer',
                                'Value': lbstring
                            },
                        ]
                    },
                    'Period': PERIOD,
                    'Stat': stat,
                    'Unit': unit
                }
            },
        ],
        StartTime=START_TIME,
        EndTime=END_TIME
    )['MetricDataResults'][0]
    
    if is_ms:
        for index in range(len(response['Values'])):
            response['Values'][index] = round(response['Values'][index] * 1000.0, 3)
    
    return response

def get_tg_metric_data(load_balancer, target_group, metric_name: str, stat: str, unit: str):
    # Hack for milliseconds
    is_ms = unit == 'Milliseconds'
    if is_ms: 
        unit = 'Seconds'

    tmp=load_balancer['LoadBalancerArn'].split(':')[-1].split('/')
    lbstring=tmp[1]+'/'+tmp[2]+'/'+tmp[3]
    tgstring=target_group['TargetGroupArn'].split(':')[-1]

    logging.info(f'Getting metric "{metric_name}" for target group "{tgstring}"')

    response = CLIENT.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'string',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': metric_name,
                        'Dimensions': [
                            {
                                'Name': 'TargetGroup',
                                'Value': tgstring
                            },
                            {
                                'Name': 'LoadBalancer',
                                'Value': lbstring
                            },
                        ]
                    },
                    'Period': PERIOD,
                    'Stat': stat,
                    'Unit': unit
                }
            },
        ],
        StartTime=START_TIME,
        EndTime=END_TIME
    )['MetricDataResults'][0]

    if is_ms:
        for index in range(len(response['Values'])):
            response['Values'][index] = round(response['Values'][index] * 1000.0, 3)
    
    return response
        


def metrics_to_latex(metrics, legends: List[str], units: str = None) -> str:
    prefix_template = '''\\begin{tikzpicture}
    \\begin{axis}[
    date coordinates in=x,
    xticklabel=\hour:\minute,
    ymin=0,
    xlabel=Time,
    ylabel={ylabel}
    ]
    '''
    plot_template = '''
    \\addplot coordinates {
        {coordinates}
    };
    '''
    legend_template = '''\legend{
        {legend}
    }
    '''
    suffix_template = '''\end{axis}
    \end{tikzpicture}\\\\\\\\'''

    label = metrics[0]['Label'].replace('_', '\\_')
    if units is not None:
        label += ' ({})'.format(units)
    prefix = prefix_template.replace('{ylabel}', label)

    core = ''
    for metric in metrics:
        coordinates = ''
        cur_date = datetime(START_TIME.year, START_TIME.month, START_TIME.day, START_TIME.hour, START_TIME.minute)
        while cur_date <= END_TIME:
            coordinate = '({}, {})\n'.format(cur_date.strftime("%m-%d-%Y %H:%M"), str(0.0))
            for index in range(len(metric['Timestamps'])):
                timestamp: datetime = metric['Timestamps'][index]
                if timestamp.hour != cur_date.hour or timestamp.minute != cur_date.minute:
                    continue
                value = metric['Values'][index]
                coordinate = '({}, {})\n'.format(timestamp.strftime("%m-%d-%Y %H:%M"), str(value))
            coordinates += coordinate
            cur_date = cur_date + PERIOD_TD
        core = core + plot_template.replace('{coordinates}', coordinates)

    legend = legend_template.replace('{legend}', ', '.join(legends))

    suffix = suffix_template


    return prefix + core + legend + suffix