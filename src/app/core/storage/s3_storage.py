import boto3
from app.core.storage.storage_base import StorageBase
from app.model.upload_model import StorageUploadResponseModel
from botocore.exceptions import ClientError
from fastapi import UploadFile
from shared.logging.logger import get_logger

logger = get_logger(__name__)


class S3Storage(StorageBase):
    def __init__(
        self,
        bucket_name: str,
        endpoint_url: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str,
    ):
        """
        Initializes the S3 storage client and ensures the specified bucket exists.

        Args:
            bucket_name (str): The name of the S3 bucket to use.
            endpoint_url (str): The endpoint URL for the S3 service.
            aws_access_key_id (str): AWS access key ID for authentication.
            aws_secret_access_key (str): AWS secret access key for authentication.
            region_name (str): AWS region where the bucket is located.

        Raises:
            Exception: If the bucket does not exist and cannot be created.
        """

        self.s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            config=boto3.session.Config(signature_version="s3v4"),
        )

        self.bucket_name = bucket_name
        try:
            logger.debug(f"Checking if bucket '{bucket_name}' exists.")
            self.s3_client.head_bucket(Bucket=bucket_name)
            logger.debug(f"Bucket '{bucket_name}' already exists.")
        except ClientError:
            try:
                logger.debug(f"Bucket '{bucket_name}' does not exist. Creating it now.")
                self.s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": "us-east-1"},
                )
                logger.debug(f"Bucket '{bucket_name}' created.")
            except Exception as err:
                logger.error(f"Error occurred: {err}")
                raise Exception(f"Failed to create bucket '{bucket_name}': {err}")

    async def upload(
        self, name: str, file: UploadFile, destination: str
    ) -> StorageUploadResponseModel:
        """
        Asynchronously uploads a file to an S3 bucket at the specified destination.

        Args:
            name (str): The name to assign to the uploaded file in the S3 bucket.
            file (UploadFile): The file object to be uploaded.
            destination (str): The destination path within the S3 bucket.

        Returns:
            StorageUploadResponseModel: An object containing details about the uploaded file,
            including its S3 path, size, and type.

        Raises:
            Exception: If the upload to S3 fails due to a client error.
        """

        try:
            self.s3_client.upload_fileobj(
                file.file, self.bucket_name, f"{destination}/{name}"
            )
            file_details = self.s3_client.head_object(
                Bucket=self.bucket_name, Key=f"{destination}/{name}"
            )

            response = StorageUploadResponseModel(
                file_path=f"s3://{self.bucket_name}/{destination}/{name}",
                file_size=file_details["ContentLength"],
                file_type=file_details.get("ContentType", "application/octet-stream"),
            )
            logger.debug(f"File uploaded to S3: {name}")
            return response
        except ClientError as err:
            logger.error(f"Failed to upload file to S3: {err}")
            raise Exception(f"Failed to upload file to S3: {err}")

    async def delete(self, name: str, destination: str) -> None:
        """
        Asynchronously deletes a file from the specified S3 bucket and destination.
        Args:
            name (str): The name of the file to delete.
            destination (str): The destination path (prefix) within the S3 bucket.
        Raises:
            Exception: If the file deletion fails due to a ClientError.
        """

        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name, Key=f"{destination}/{name}"
            )
            logger.debug(f"File deleted from S3: {name}")
        except ClientError as err:
            logger.error(f"Failed to delete file from S3: {err}")
            raise Exception(f"Failed to delete file from S3: {err}")
