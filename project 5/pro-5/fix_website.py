import boto3
import json

s3 = boto3.client('s3')

bucket_name = "sanskruti-static-site-001"

policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicRead",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*"
        }
    ]
}

s3.put_bucket_policy(
    Bucket=bucket_name,
    Policy=json.dumps(policy)
)

print("Bucket policy applied")