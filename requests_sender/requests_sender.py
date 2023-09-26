import requests, threading, time, logging, boto3, sys

BASE_URL = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def call_endpoint_http(url):
    response = requests.get(url)

def thread_1_fct(url):
    logging.info('> Thread 1: Started.')
    for i in range(1000):
        call_endpoint_http(url)
    logging.info('> Thread 1: Done.')

def thread_2_fct(url):
    logging.info('> Thread 2: Started.')
    for i in range(500):
        call_endpoint_http(url)
    logging.info('> Thread 2: Waiting 60 seconds.')
    time.sleep(60)
    for i in range(1000):
        call_endpoint_http(url)
    logging.info('> Thread 2: Done.')

def get_load_balancer(name: str):
    elbv2 = boto3.client('elbv2')
    load_balancers = elbv2.describe_load_balancers()['LoadBalancers']
    for load_balancer in load_balancers:
        if load_balancer['LoadBalancerName'] == name:
            return load_balancer
    logging.error('Unable to find load balancer.')
    sys.exit(1)

if __name__ == "__main__":

    # Retrieve base URL
    logging.info('Retrieving load balancer base URL...')
    load_balancer = get_load_balancer('tp1')
    dns_name = load_balancer['DNSName']
    BASE_URL = f'http://{dns_name}'
    logging.info('  ' + BASE_URL)

    # Send requests
    for cluster in ('cluster1', 'cluster2'):
        logging.info('Sending requests to ' + cluster)
        url = BASE_URL + '/' + cluster
        thread_1 = threading.Thread(target=thread_1_fct, args=(url, ))
        thread_2 = threading.Thread(target=thread_2_fct, args=(url, ))
        thread_1.start()
        thread_2.start()
        thread_1.join()
        thread_2.join()
