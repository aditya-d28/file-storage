import os

from app.core.storage.storage_base import StorageBase
from app.model.upload_model import StorageUploadResponseModel
from fastapi import UploadFile
from shared.logging.logger import get_logger

logger = get_logger(__name__)


class FileStorage(StorageBase):
    def __init__(self, bucket_name: str, **kwargs):
        """
        Initializes the file storage with the specified bucket name.

        If the directory specified by `bucket_name` does not exist, it is created.

        Args:
            bucket_name (str): The name of the directory to use as the storage bucket.
            **kwargs: Additional keyword arguments.

        Logs:
            Logs the creation of the base path if it does not already exist.
        """
        self.bucket_name = bucket_name
        if not os.path.exists(bucket_name):
            os.makedirs(bucket_name)
            logger.info(f"Base path created: {bucket_name}")

    async def upload(self, name: str, file: UploadFile, destination: str = "") -> StorageUploadResponseModel:
        """
        Asynchronously uploads a file to the local storage.

        Args:
            name (str): The name to save the file as.
            file (UploadFile): The file object to upload.
            destination (str, optional): The destination directory within the storage bucket. Defaults to "".

        Returns:
            StorageUploadResponseModel: An object containing details about the uploaded file, such as file path, size, and type.

        Raises:
            Exception: If the file upload fails for any reason.
        """

        file_path = os.path.join(self.bucket_name, destination, name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            with open(file_path, "wb") as f:
                contents = await file.read()
                f.write(contents)
            logger.info(f"File uploaded to local storage: {file_path}")

            response = StorageUploadResponseModel(
                file_path=file_path,
                file_size=file.file_size if hasattr(file, "file_size") else os.path.getsize(file_path),
                file_type=file.content_type if hasattr(file, "content_type") else "application/octet-stream",
            )
            return response
        except Exception as err:
            logger.error(f"Failed to upload file to local storage: {err}")
            raise Exception(f"Failed to upload file to local storage: {err}")

    async def delete(self, name: str, destination: str) -> None:
        """
        Asynchronously deletes a file from the local storage.

        Args:
            name (str): The name of the file to delete.
            destination (str): The directory path within the storage bucket where the file is located.

        Raises:
            Exception: If the file cannot be deleted due to an OSError.
        """

        try:
            os.remove(os.path.join(self.bucket_name, destination, name))
            logger.info(f"File deleted from local storage: {name} at {destination}")
        except OSError as err:
            logger.error(f"Failed to delete file from local storage: {err}")
            raise Exception(f"Failed to delete file from local storage: {err}")
