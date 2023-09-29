from typing import Any, Dict
from google.cloud import storage
from google.oauth2 import service_account
import json
import pickle
from PIL import Image
import numpy as np
import os
import io
import shutil
from rich.console import Console
from alectio_sdk.sdk.utils import get_storage_credentials


console = Console()


   
class GCP_Storage:
    exp_token : str
    gcpStorageClient: None

    # def init :- experimenttoken
    def __init__(self, exp_token):
        self.exp_token = exp_token
        storage_info=get_storage_credentials(exp_token=exp_token)
    
        storage_info = json.loads(storage_info)
        credentials = service_account.Credentials.from_service_account_info(storage_info)
        self.gcpStorageClient = storage.Client(project=None, credentials=credentials)
        

    def download_file(
        self, storage_bucket: str, object_key: str, format: str, dest_path: str
    ):
        bucket = self.gcpStorageClient.get_bucket(storage_bucket)
        blob = bucket.blob(object_key)
        if format in ["jpg", "png", "jpeg"]:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            blob.download_to_filename(dest_path)
        if format == "zip":
            done = False
            with console.status("[bold green]Loading dataset from cloud...") as status:
                while not done:
                    blob.download_to_filename(dest_path + ".zip")
                    shutil.unpack_archive(dest_path + ".zip", dest_path)
                    done = True

    def read_file(self, storage_bucket: str, object_key: str, format: str):
        # print('we are hitting this function!!!!')
        # print(object_key)
        # print(storage_bucket)
        bucket = self.gcpStorageClient.get_bucket(storage_bucket)
        blob = bucket.blob(object_key)

        if format == "json":
            data = json.loads(blob.download_as_string(client=None))
        if format == "pkl":
            data = pickle.loads(blob.download_as_string(client=None))
        if format == "text":
            data = blob.download_as_string(client=None)
        return data

    def upload_object(
        self, storage_bucket: str, object: Any, object_key: str, format: str
    ):
        bucket = self.gcpStorageClient.get_bucket(storage_bucket)
        blob = bucket.blob(object_key)

        if format == "json":
            blob.upload_from_string(data=json.dumps(object))
        if format == "pkl":
            blob.upload_from_string(data=pickle.dumps(object))
        if format == "txt":
            blob.upload_from_string(data=object)
        if format in ["png", "jpg"]:
            img = Image.fromarray(np.uint8(object)).convert("RGB")
            blob.upload_from_string(img.tobytes(), content_type="image/jpeg")

    def upload_file(self, storage_bucket: str, file_path: str, object_key: str):
        bucket = self.gcpStorageClient.get_bucket(storage_bucket)
        blob = bucket.blob(object_key)
        blob.upload_from_filename(file_path)
