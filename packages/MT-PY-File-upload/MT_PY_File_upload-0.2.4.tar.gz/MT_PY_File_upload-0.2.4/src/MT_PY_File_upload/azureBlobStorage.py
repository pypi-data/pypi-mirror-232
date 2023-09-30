from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError


def uploadToBlobStorage(file_path, file_name,storage_account_key,storage_account_name,container_name,connection_string):
    try:
        storage_account_key = storage_account_key
        storage_account_name=storage_account_name
        container_name = container_name
        connection_string=connection_string
        
        blob_service_client=BlobServiceClient.from_connection_string(connection_string)
        blob_client=blob_service_client.get_blob_client(container=container_name,blob=file_name)

        with open(file_path,"rb") as data:
            blob_client.upload_blob(data)
        return True
    except ResourceExistsError:
        new_file_name = generate_unique_file_name(file_name)
        uploadToBlobStorage(file_path, new_file_name)
        print(f"A blob with the name '{file_name}' already exists. Renamed to '{new_file_name}' and uploaded.")
        return True
    except Exception as e:
        return False
def generate_unique_file_name(file_name):
    import datetime
    import uuid

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4()).replace("-", "")[:8]
    return f"{file_name}_{timestamp}_{unique_id}"

