import os
import base64
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any

import boto3 # type: ignore
from google.cloud import storage # type: ignore
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions

from dotenv import load_dotenv
load_dotenv()

# Constants
ONE_MB = 1024 * 1024

class StorageConfig:
    def __init__(self):
        self.BUCKET_NAME = os.getenv("BUCKET_NAME")
        self.is_using_s3 = os.getenv("IS_USING_S3") == "true"
        self.is_using_gcs = os.getenv("IS_USING_GCS") == "true"
        self.is_using_azure = os.getenv("IS_USING_AZURE") == "true"
        
        # AWS configs
        self.aws_region = os.getenv("APP_AWS_REGION")
        self.aws_access_key = os.getenv("APP_AWS_ACCESS_KEY")
        self.aws_secret_key = os.getenv("APP_AWS_SECRET_KEY")
        self.dev_aws_endpoint = os.getenv("DEV_AWS_ENDPOINT")
        
        # GCS configs
        self.gcs_project_id = os.getenv("APP_GCS_PROJECT_ID")
        self.gcs_client_email = os.getenv("APP_GCS_CLIENT_EMAIL")
        self.gcs_private_key = os.getenv("APP_GCS_PRIVATE_KEY")
        
        # Azure configs
        self.azure_storage_account = os.getenv("APP_AZURE_STORAGE_ACCOUNT")
        self.azure_storage_key = os.getenv("APP_AZURE_STORAGE_ACCESS_KEY")

class StorageService:
    def __init__(self):
        self.config = StorageConfig()
        self.client = self._initialize_storage()

    def _initialize_storage(self):
        if sum([self.config.is_using_s3, self.config.is_using_gcs, self.config.is_using_azure]) > 1:
            raise ValueError("Multiple storage configurations detected. Please use only one.")

        if self.config.is_using_s3:
            return boto3.client(
                's3',
                region_name=self.config.aws_region,
                aws_access_key_id=self.config.aws_access_key,
                aws_secret_access_key=self.config.aws_secret_key,
                endpoint_url=self.config.dev_aws_endpoint,
                # force_path_style=True
            )
        
        elif self.config.is_using_gcs:
            private_key = base64.b64decode(self.config.gcs_private_key).decode('utf-8')
            return storage.Client.from_service_account_info({
                "project_id": self.config.gcs_project_id,
                "client_email": self.config.gcs_client_email,
                "private_key": private_key
            })
        
        elif self.config.is_using_azure:
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.config.azure_storage_account};AccountKey={self.config.azure_storage_key};EndpointSuffix=core.windows.net"
            return BlobServiceClient.from_connection_string(connection_string)
        
        raise ValueError("No storage configuration found")

    async def create_request(self, prefix: str, key: str, content_type: Optional[str] = None, size: int = 30) -> Dict[str, Any]:
        if not self.config.BUCKET_NAME:
            raise ValueError("No BUCKET_NAME found")

        fields = {"key": key}
        if content_type:
            fields["Content-Type"] = content_type

        if self.config.is_using_s3:
            response = self.client.generate_presigned_post(
                Bucket=self.config.BUCKET_NAME,
                Key=key,
                Fields=fields,
                Conditions=[
                    {"bucket": self.config.BUCKET_NAME},
                    ["starts-with", "$key", prefix],
                    ["content-length-range", 0, size * ONE_MB]
                ],
                ExpiresIn=60
            )
            return {"post": {**response, "uploadType": "multipart"}}

        elif self.config.is_using_gcs:
            bucket = self.client.bucket(self.config.BUCKET_NAME)
            blob = bucket.blob(key)
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=1),
                method="POST",
                content_type=content_type
            )
            return {"post": {"url": url, "fields": fields, "uploadType": "multipart"}}

        elif self.config.is_using_azure:
            url = self._create_azure_url(key, "c")
            return {
                "put": {
                    "url": url,
                    "headers": {
                        "x-ms-blob-type": "BlockBlob",
                        "Content-Type": content_type
                    },
                    "fields": fields,
                    "uploadType": "raw"
                }
            }
        raise Exception("Unsupported storage configuration")

    async def sign_url(self, key: str, action: str = "read", project_id: Optional[str] = None) -> str:
        if not self.config.BUCKET_NAME:
            raise ValueError("No BUCKET_NAME found")

        if self.config.is_using_s3:
            return self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.config.BUCKET_NAME, 'Key': key},
                ExpiresIn=3600
            )

        elif self.config.is_using_gcs:
            bucket = self.client.bucket(self.config.BUCKET_NAME)
            blob = bucket.blob(key)
            return blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=1),
                method="GET" if action == "read" else "PUT"
            )

        elif self.config.is_using_azure:
            return self._create_azure_url(
                key,
                "r" if action == "read" else "w",
                expiry_ms=3600000
            )
        raise Exception("Unsupported storage configuration")

    def _create_azure_url(self, key: str, permission: str, expiry_ms: int = 60000) -> str:
        if not self.config.azure_storage_account or not self.config.azure_storage_key:
            raise ValueError("Azure storage credentials not configured")

        sas_token = generate_blob_sas(
            account_name=self.config.azure_storage_account,
            container_name=self.config.BUCKET_NAME,
            blob_name=key,
            account_key=self.config.azure_storage_key,
            permission=BlobSasPermissions(read='r' in permission, create='c' in permission, write='w' in permission),
            expiry=datetime.utcnow() + timedelta(milliseconds=expiry_ms)
        )

        return f"https://{self.config.azure_storage_account}.blob.core.windows.net/{self.config.BUCKET_NAME}/{key}?{sas_token}"

storage_service = StorageService()