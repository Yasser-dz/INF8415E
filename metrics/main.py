
# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

# Do imports
import sys, json, load_balancers, cloudwatch

# Retrieve load balancer
load_balancer = load_balancers.get_load_balancer('tp1')
cluster1 = load_balancers.get_target_group('cluster1')
cluster2 = load_balancers.get_target_group('cluster2')

metrics_text = []
metrics = {}

# RequestCount, load balancer
metrics['RequestCount'] = {
    'elb': cloudwatch.get_elb_metric_data(load_balancer, 'RequestCount', 'Sum', 'Count'),
    'cluster1': cloudwatch.get_tg_metric_data(load_balancer, cluster1, 'RequestCount', 'Sum', 'Count'),
    'cluster2': cloudwatch.get_tg_metric_data(load_balancer, cluster2, 'RequestCount', 'Sum', 'Count')
}
metrics_text.append(cloudwatch.metrics_to_latex([metrics['RequestCount']['elb']], ['Load Balancer']))

# RequestCount, cluster1 vs cluster2
metrics_text.append(cloudwatch.metrics_to_latex([metrics['RequestCount']['cluster1'], metrics['RequestCount']['cluster2']], ['Cluster 1 (t2)', 'Cluster 2 (m4)']))

# HTTP 2XX, cluster1 vs cluster2 vs load balancer
metrics['HTTPCode_Target_2XX_Count'] = {
    'cluster1': cloudwatch.get_tg_metric_data(load_balancer, cluster1, 'HTTPCode_Target_2XX_Count', 'Sum', 'Count'),
    'cluster2': cloudwatch.get_tg_metric_data(load_balancer, cluster2, 'HTTPCode_Target_2XX_Count', 'Sum', 'Count')
}
metrics_text.append(cloudwatch.metrics_to_latex([metrics['HTTPCode_Target_2XX_Count']['cluster1'], metrics['HTTPCode_Target_2XX_Count']['cluster2']], ['Cluster 1 (t2)', 'Cluster 2 (m4)']))

# HTTP 4XX, cluster1 vs cluster2 vs load balancer
metrics['HTTPCode_Target_4XX_Count'] = {
    'cluster1': cloudwatch.get_tg_metric_data(load_balancer, cluster1, 'HTTPCode_Target_4XX_Count', 'Sum', 'Count'),
    'cluster2': cloudwatch.get_tg_metric_data(load_balancer, cluster2, 'HTTPCode_Target_4XX_Count', 'Sum', 'Count')
}
metrics_text.append(cloudwatch.metrics_to_latex([metrics['HTTPCode_Target_4XX_Count']['cluster1'], metrics['HTTPCode_Target_4XX_Count']['cluster2']], ['Cluster 1 (t2)', 'Cluster 2 (m4)']))

# HTTP 5XX, cluster1 vs cluster2 vs load balancer
metrics['HTTPCode_Target_5XX_Count'] = {
    'cluster1': cloudwatch.get_tg_metric_data(load_balancer, cluster1, 'HTTPCode_Target_5XX_Count', 'Sum', 'Count'),
    'cluster2': cloudwatch.get_tg_metric_data(load_balancer, cluster2, 'HTTPCode_Target_5XX_Count', 'Sum', 'Count')
}
metrics_text.append(cloudwatch.metrics_to_latex([metrics['HTTPCode_Target_5XX_Count']['cluster1'], metrics['HTTPCode_Target_5XX_Count']['cluster2']], ['Cluster 1 (t2)', 'Cluster 2 (m4)']))

# TargetResponseTime, cluster1 vs cluster2
metrics['TargetResponseTime'] = {
    'cluster1': cloudwatch.get_tg_metric_data(load_balancer, cluster1, 'TargetResponseTime', 'Average', 'Milliseconds'),
    'cluster2': cloudwatch.get_tg_metric_data(load_balancer, cluster2, 'TargetResponseTime', 'Average', 'Milliseconds')
}
metrics_text.append(cloudwatch.metrics_to_latex([metrics['TargetResponseTime']['cluster1'], metrics['TargetResponseTime']['cluster2']], ['Cluster 1 (t2)', 'Cluster 2 (m4)'], 'ms'))

# Write latex to file
with open("metrics_latex.txt", "w") as file:
    file.write('\n'.join(metrics_text))
logging.info('Metrics in latex format have been written to metrics_latex.txt!')

# Write raw responses to file
with open("metrics_raw.txt", "w") as file:
    file.write(json.dumps(metrics, indent=4, sort_keys=True, default=str))
logging.info('Raw metrics have been written to metrics_raw.txt!')

sys.exit(0)