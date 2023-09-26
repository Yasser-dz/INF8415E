from boto3_type_annotations.ec2 import ServiceResource, Vpc

def get_default_vpc(ec2: ServiceResource) -> Vpc:
    for vpc in ec2.vpcs.all():
        if vpc.is_default:
            return vpc
