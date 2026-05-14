import boto3
import json

s3 = boto3.client('s3')

bucket_name = "sanskruti-static-site-001"  # ✅ same as you want

# Create bucket (will fail if already exists)
try:
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            'LocationConstraint': 'ap-south-1'
        }
    )
    print("Bucket created")
except:
    print("Bucket already exists, continuing...")

# Upload file
s3.upload_file("index.html", bucket_name, "index.html")
print("Website file uploaded")

# Enable static website hosting
s3.put_bucket_website(
    Bucket=bucket_name,
    WebsiteConfiguration={
        'IndexDocument': {'Suffix': 'index.html'}
    }
)
print("Static website hosting enabled")

# ✅ Correct JSON policy
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
        }
    ]
}

s3.put_bucket_policy(
    Bucket=bucket_name,
    Policy=json.dumps(policy)
)

print("Bucket made public")

# Final URL
print(f"\nWebsite URL: http://{bucket_name}.s3-website-ap-south-1.amazonaws.com")