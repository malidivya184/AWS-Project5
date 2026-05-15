import boto3
import os
import mimetypes
import time
import json

# ---------------------------------------------------
# AWS CLIENT
# ---------------------------------------------------

s3 = boto3.client('s3', region_name='ap-south-1')

# ---------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------

BUCKET_NAME = f"divya-static-website-{int(time.time())}"

WEBSITE_FOLDER = "website"

REGION = "ap-south-1"

# ---------------------------------------------------
# CREATE WEBSITE FOLDER
# ---------------------------------------------------

print("Creating Website Folder...")

os.makedirs(WEBSITE_FOLDER, exist_ok=True)

# ---------------------------------------------------
# CREATE index.html
# ---------------------------------------------------

index_html = """
<!DOCTYPE html>
<html>
<head>
    <title>AWS Static Website</title>

    <style>

        body{
            font-family: Arial;
            text-align:center;
            background:#f4f4f4;
            padding-top:100px;
        }

        h1{
            color:#ff9900;
        }

        p{
            font-size:20px;
        }

    </style>

</head>

<body>

    <h1>Static Website Hosted on AWS S3</h1>

    <p>Deployed using Python Boto3 Automation</p>

</body>
</html>
"""

with open(f"{WEBSITE_FOLDER}/index.html", "w") as file:
    file.write(index_html)

# ---------------------------------------------------
# CREATE error.html
# ---------------------------------------------------

error_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Error</title>
</head>

<body style="text-align:center;padding-top:100px;font-family:Arial;">

    <h1>404 Error</h1>

    <p>Page Not Found</p>

</body>
</html>
"""

with open(f"{WEBSITE_FOLDER}/error.html", "w") as file:
    file.write(error_html)

print("Website Files Created")

# ---------------------------------------------------
# CREATE S3 BUCKET
# ---------------------------------------------------

print("Creating S3 Bucket...")

try:

    s3.create_bucket(
        Bucket=BUCKET_NAME,
        CreateBucketConfiguration={
            'LocationConstraint': REGION
        }
    )

    print("Bucket Created:", BUCKET_NAME)

except Exception as e:

    print("Bucket Error")
    print(e)

# ---------------------------------------------------
# DISABLE BLOCK PUBLIC ACCESS
# ---------------------------------------------------

print("Configuring Public Access...")

s3.put_public_access_block(
    Bucket=BUCKET_NAME,
    PublicAccessBlockConfiguration={
        'BlockPublicAcls': False,
        'IgnorePublicAcls': False,
        'BlockPublicPolicy': False,
        'RestrictPublicBuckets': False
    }
)

print("Public Access Enabled")

# ---------------------------------------------------
# ENABLE STATIC WEBSITE HOSTING
# ---------------------------------------------------

print("Enabling Static Website Hosting...")

s3.put_bucket_website(
    Bucket=BUCKET_NAME,
    WebsiteConfiguration={
        'IndexDocument': {
            'Suffix': 'index.html'
        },
        'ErrorDocument': {
            'Key': 'error.html'
        }
    }
)

print("Static Website Hosting Enabled")

# ---------------------------------------------------
# ADD BUCKET POLICY
# ---------------------------------------------------

print("Adding Bucket Policy...")

bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{BUCKET_NAME}/*"
        }
    ]
}

s3.put_bucket_policy(
    Bucket=BUCKET_NAME,
    Policy=json.dumps(bucket_policy)
)

print("Bucket Policy Added")

# ---------------------------------------------------
# UPLOAD WEBSITE FILES
# ---------------------------------------------------

print("Uploading Website Files...")

for file_name in os.listdir(WEBSITE_FOLDER):

    file_path = os.path.join(WEBSITE_FOLDER, file_name)

    content_type = mimetypes.guess_type(file_path)[0]

    s3.upload_file(
        file_path,
        BUCKET_NAME,
        file_name,
        ExtraArgs={
            'ContentType': content_type
        }
    )

    print(f"Uploaded: {file_name}")

# ---------------------------------------------------
# WEBSITE URL
# ---------------------------------------------------

website_url = f"http://{BUCKET_NAME}.s3-website-{REGION}.amazonaws.com"

# ---------------------------------------------------
# SUCCESS MESSAGE
# ---------------------------------------------------

print("\n======================================")
print("STATIC WEBSITE DEPLOYED SUCCESSFULLY")
print("======================================")

print("Bucket Name:", BUCKET_NAME)

print("\nWebsite URL:")
print(website_url)