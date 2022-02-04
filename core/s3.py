import boto3
import os

ACCESS_KEY = os.environ.get('S3_ACCESS_KEY', "fNhUxNGK2FGafTqy")
SECRET_KEY = os.environ.get('S3_SECRET_KEY', "MjhYNvJ72VaAG9fmjYDuAhg8T7vW6d3v")

client = boto3.client("s3",
                      endpoint_url="https://s3.azat.ai",
                      aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY
                      )
BUCKET = "public"
