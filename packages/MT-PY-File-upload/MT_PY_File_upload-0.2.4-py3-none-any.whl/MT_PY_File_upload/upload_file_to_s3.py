import boto3
import os



def Upload_file_to_s3(file_path, bucket_name, object_name,aws_access_key,aws_secret_key,region_name):
    
    # AWS credentials and region

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