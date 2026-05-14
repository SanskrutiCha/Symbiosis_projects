import boto3
import json
import zipfile
import uuid
import time

region = "ap-south-1"

bucket_name = "serverless-rekognition-" + str(uuid.uuid4())
lambda_name = "rekognition-trigger-" + str(uuid.uuid4())
role_name = "rekognition-role-" + str(uuid.uuid4())

iam = boto3.client("iam")
s3 = boto3.client("s3", region_name=region)
lambda_client = boto3.client("lambda", region_name=region)

# --------------------------
# 1. Create S3 Bucket
# --------------------------
if region == "us-east-1":
    s3.create_bucket(Bucket=bucket_name)
else:
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": region}
    )

print("S3 Bucket Created:", bucket_name)

# --------------------------
# 2. Create IAM Role
# --------------------------
assume_role_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }
    ]
}

role = iam.create_role(
    RoleName=role_name,
    AssumeRolePolicyDocument=json.dumps(assume_role_policy)
)

iam.attach_role_policy(
    RoleName=role_name,
    PolicyArn="arn:aws:iam::aws:policy/AmazonRekognitionFullAccess"
)

iam.attach_role_policy(
    RoleName=role_name,
    PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
)

iam.attach_role_policy(
    RoleName=role_name,
    PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
)

print("IAM Role Created:", role_name)

# Wait for IAM propagation
time.sleep(30)

# --------------------------
# 3. Create Lambda Code
# --------------------------
lambda_code = """
import boto3

rekognition = boto3.client('rekognition')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    response = rekognition.detect_faces(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        Attributes=['DEFAULT']
    )

    face_count = len(response['FaceDetails'])
    print("Faces detected:", face_count)

    return {"faces_detected": face_count}
"""

with open("lambda_function.py", "w") as f:
    f.write(lambda_code)

with zipfile.ZipFile("lambda_function.zip", "w") as z:
    z.write("lambda_function.py")

with open("lambda_function.zip", "rb") as f:
    zipped_code = f.read()

# --------------------------
# 4. Create Lambda Function
# --------------------------
lambda_client.create_function(
    FunctionName=lambda_name,
    Runtime="python3.12",
    Role=role["Role"]["Arn"],
    Handler="lambda_function.lambda_handler",
    Code={"ZipFile": zipped_code},
    Timeout=15,
    MemorySize=128,
    Publish=True
)

print("Lambda Created:", lambda_name)

# --------------------------
# 5. Allow S3 to Invoke Lambda
# --------------------------
lambda_client.add_permission(
    FunctionName=lambda_name,
    StatementId="s3invoke",
    Action="lambda:InvokeFunction",
    Principal="s3.amazonaws.com",
    SourceArn=f"arn:aws:s3:::{bucket_name}"
)

# --------------------------
# 6. Configure S3 Trigger
# --------------------------
lambda_arn = lambda_client.get_function(FunctionName=lambda_name)["Configuration"]["FunctionArn"]

notification_configuration = {
    "LambdaFunctionConfigurations": [
        {
            "LambdaFunctionArn": lambda_arn,
            "Events": ["s3:ObjectCreated:*"]
        }
    ]
}

s3.put_bucket_notification_configuration(
    Bucket=bucket_name,
    NotificationConfiguration=notification_configuration
)

print("S3 Trigger Configured")
print("--------------------------------------------------")
print("SETUP COMPLETE")
print("Upload an image to this bucket:", bucket_name)
print("Then check CloudWatch logs for Lambda output.")