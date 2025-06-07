from app.core.storage.storage_base import StorageBase
from app.model.upload_model import StorageUploadResponseModel
from fastapi import UploadFile
from google.api_core.exceptions import NotFound
from google.cloud import storage
from shared.logging.logger import get_logger

logger = get_logger(__name__)


class GoogleCloudStorage(StorageBase):
    def __init__(self, bucket_name: str, location: str):
        """
        Initializes the Google Cloud Storage client and ensures the specified bucket exists.

        Args:
            bucket_name (str): The name of the Google Cloud Storage bucket to use.
            location (str): The location where the bucket should be created if it does not exist.

        Raises:
            Exception: If the bucket does not exist and cannot be created.
        """
        self.client = (
            storage.Client()
        )  # Authentication is handled by the environment variable GOOGLE_APPLICATION_CREDENTIALS
        try:
            logger.debug(f"Checking if bucket '{bucket_name}' exists.")
            self.bucket = self.client.get_bucket(bucket_name)
            logger.debug(f"Bucket '{bucket_name}' already exists.")
        except NotFound:
            try:
                logger.debug(f"Bucket '{bucket_name}' does not exist. Creating it now.")
                self.bucket = self.client.create_bucket(bucket_name, location=location)
                logger.debug(f"Bucket '{bucket_name}' created in location '{location}'.")
            except Exception as err:
                logger.error(f"Error occurred: {err}")
                raise Exception(f"Failed to create bucket '{bucket_name}': {err}")
        except Exception as err:
            logger.error(f"Error occurred: {err}")
            raise Exception(f"Failed to create bucket '{bucket_name}': {err}")

    async def upload(self, name: str, file: UploadFile, destination: str) -> StorageUploadResponseModel:
        """
        Uploads a file to Google Cloud Storage.

        Args:
            name (str): The name to assign to the uploaded file in the storage bucket.
            file (UploadFile): The file object to upload, typically from a FastAPI request.
            destination (str): The destination folder or path within the bucket.

        Returns:
            StorageUploadResponseModel: An object containing the file path, size, and type of the uploaded file.

        Raises:
            Exception: If the upload process fails for any reason.
        """

        try:
            blob = self.bucket.blob(f"{destination}/{name}")
            blob.upload_from_file(file.file, content_type=file.content_type)
            blob.reload()

            response = StorageUploadResponseModel(
                file_path=f"gs://{self.bucket.name}/{destination}/{name}",
                file_size=blob.size() or 0,
                file_type=blob.content_type or "application/octet-stream",
            )
            logger.debug(f"File uploaded to Google Cloud Storage: {name}")
            return response
        except Exception as err:
            logger.error(f"Failed to upload file to Google Cloud Storage: {err}")
            raise Exception(f"Failed to upload file to Google Cloud Storage: {err}")

    async def delete(self, name: str, destination: str) -> None:
        """
        Deletes a file from the specified destination in Google Cloud Storage.
        Args:
            name (str): The name of the file to delete.
            destination (str): The destination path or folder in the bucket where the file is stored.
        Raises:
            Exception: If the file deletion fails for any reason.
        """

        try:
            blob = self.bucket.blob(f"{destination}/{name}")
            blob.delete()
            logger.info(f"File deleted from Google Cloud Storage: {name}")
        except Exception as err:
            logger.error(f"Failed to delete file from Google Cloud Storage: {err}")
            raise Exception(f"Failed to delete file from Google Cloud Storage: {err}")
