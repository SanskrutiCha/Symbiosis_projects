import boto3

ec2 = boto3.resource('ec2')

instances = ec2.create_instances(
    ImageId='ami-04b31f2b03a63f99c',
    MinCount=1,
    MaxCount=1,
    InstanceType='t3.micro',
    KeyName='sanskruti-keypair'
)

print("EC2 Instance Created")

s3 = boto3.client('s3')

bucket_name = "sanskruti-aws-project-001"

s3.create_bucket(
    Bucket=bucket_name,
    CreateBucketConfiguration={
        'LocationConstraint': 'ap-south-1'
    }
)

print("S3 Bucket Created")

# 🔽 ADD THIS PART (FILE UPLOAD)

file_name = "test.txt"        # file in your local folder
s3_key = "test.txt"          # name in S3

s3.upload_file(file_name, bucket_name, s3_key)

print("File uploaded to S3")