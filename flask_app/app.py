from flask import Flask
import logging, requests, json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

# Get instance ID
try:
    INSTANCE_ID = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
except:
    INSTANCE_ID = 'unknown'
logging.info(f'Instance ID: {INSTANCE_ID}')

# Prepare response
CLUSTER_RESPONSE = json.dumps({'instance_id': INSTANCE_ID})

# Create Flask app
app = Flask(__name__)

# Cluster 1
@app.route('/cluster1')
def cluster_1():
    return CLUSTER_RESPONSE

# Cluster2
@app.route('/cluster2')
def cluster_2():
    return CLUSTER_RESPONSE

# Ping
@app.route('/ping')
def ping():
    return 'pong'

# Start in production mode
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=80)
