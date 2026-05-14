import boto3
import uuid
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

region = "ap-south-1"

# Local image path
image_path = r"C:\Users\manak\Desktop\Symboysis\AWS_Rekognization\image.png"

# S3 object name (ONLY filename, not full path)
object_name = "image.png"

bucket_name = "rekognition-demo-" + str(uuid.uuid4())

s3 = boto3.client("s3", region_name=region)
rekognition = boto3.client("rekognition", region_name=region)

# Create bucket
if region == "us-east-1":
    s3.create_bucket(Bucket=bucket_name)
else:
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": region}
    )

# Upload image to S3
s3.upload_file(image_path, bucket_name, object_name)

# Detect faces
response = rekognition.detect_faces(
    Image={
        "S3Object": {
            "Bucket": bucket_name,
            "Name": object_name
        }
    },
    Attributes=["DEFAULT"]
)

face_details = response["FaceDetails"]
face_count = len(face_details)

print("Bucket Created:", bucket_name)
print("Image Uploaded:", object_name)
print("Number of Faces Detected:", face_count)

# Draw bounding boxes
image = Image.open(image_path)
draw = ImageDraw.Draw(image)

width, height = image.size

for face in face_details:
    box = face["BoundingBox"]

    left = box["Left"] * width
    top = box["Top"] * height
    box_width = box["Width"] * width
    box_height = box["Height"] * height

    draw.rectangle(
        [(left, top), (left + box_width, top + box_height)],
        outline="red",
        width=3
    )

# Show image with bounding boxes
plt.imshow(image)
plt.axis("off")
plt.title(f"Faces Detected: {face_count}")
plt.show()