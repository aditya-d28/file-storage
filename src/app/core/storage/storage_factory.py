from app.core.config import settings
from app.core.storage.file_storage import FileStorage
from app.core.storage.google_cloud_storage import GoogleCloudStorage
from app.core.storage.s3_storage import S3Storage
from app.core.storage.storage_base import StorageBase


class StorageFactory:
    @staticmethod
    def get_storage(storage_type: str, bucket_name: str) -> StorageBase:
        """
        Factory method to instantiate and return a storage backend based on the specified storage type.

        Args:
            storage_type (str): The type of storage backend to use. Supported values are "local", "s3", and "gcs".
            bucket_name (str): The name of the storage bucket to use.

        Returns:
            StorageBase: An instance of the appropriate storage backend class.

        Raises:
            ValueError: If an unknown storage type is provided.
        """

        if storage_type == "local":
            return FileStorage(bucket_name=bucket_name)
        elif storage_type == "s3":
            return S3Storage(
                bucket_name=bucket_name,
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.STORAGE_AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.STORAGE_AWS_SECRET_ACCESS_KEY,
                region_name=settings.STORAGE_REGION_NAME,
            )
        elif storage_type == "gcs":
            return GoogleCloudStorage(
                bucket_name=bucket_name, location=settings.STORAGE_GCS_LOCATION
            )
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")
