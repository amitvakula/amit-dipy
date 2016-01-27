import boto3
from time import sleep

def check_existing():
	ec2 = boto3.resource('ec2')
	ec2.instances.filter(Filters=[{
		'Name' : 'instance-state-name',
		'Values' : ['running']
	}])
	for i in response:
		return False
	return True

def setup_cluster(num_instances=1, machine_image='ami-12345678', key='dotpem', security_group_id='sg-12345678', instance_profile='arn:aws:iam::123456789012:instance-profile/sample'):	
	
	ec2 = boto3.client('ec2')
	id_set = set()
	
	for i in range(num_instances):
		pre_USER_DATA = '''#!/bin/bash
		python /home/ec2-user/quipc_tools/tracker.py ''' + str(i)

		USER_DATA = b64encode(pre_USER_DATA)		
		response = ec2.request_spot_instances(
			SpotPrice= '.02',
			InstanceCount=1,
			Type='one-time',
			LaunchSpecification={
				'ImageId': machine_image,
				'InstanceType': 'm4.large',
				'KeyName' : key,
				'UserData': USER_DATA,
				'SecurityGroupIds' : [security_group_id],
				'IamInstanceProfile' : {
					'Arn' : instance_profile
				}
			}
		)

		response = response['SpotInstanceRequests']
		id_set.add(response[0]['InstanceId'])

	instance_set = set()
	while len(instance_set) < len(id_set):
		response = ec2.describe_spot_instance_requests(SpotInstanceRequestIds=list(id_set))
		response = response['SpotInstanceRequests']
		for resp in response:
			status = resp['Status']['Code']
			if status == 'fulfilled':
				instance_set.add(resp['InstanceId'])
		sleep(3)
	return instance_set

def s3_upload(in_file_path, bucket='track-input'):
	s3 = boto3.client('s3')
	s3.upload_file(in_file_path,bucket,in_file_path.split('/')[:-1])

def s3_download(identifier, out_file_path, bucket='track-input'):
	s3 = boto3.client('s3')
	s3.download_file(BUCKET, identifier + '_out.trk', out_file_path)

def close_cluster(instance_set):
	ec2 = boto3.client('ec2')
	response = client.terminate_instances(
		InstanceIds=list(instance_set)
	)

if __name__ == "__main__":
    setup_cluster()