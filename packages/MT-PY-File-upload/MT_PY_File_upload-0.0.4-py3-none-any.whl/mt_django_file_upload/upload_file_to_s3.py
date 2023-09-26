import boto3
import os
from dotenv import load_dotenv
load_dotenv()


def Upload_file_to_s3(file_path, bucket_name, object_name):
    

    # AWS credentials and region
    # Note: the .env file should be in same directory..
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID',default=None)
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY',default=None)
    region_name = os.getenv('AWS_S3_REGION_NAME',default=None)

    # Create an AWS session
    session = boto3.Session(aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

    s3_client = session.client('s3')

    try:
        # # Upload the file to S3 with the generated object key
        s3_client.upload_file(file_path, bucket_name, object_name)
        print("File uploaded successfully.")
        return True
    except Exception as e:
        print(e)
        return False