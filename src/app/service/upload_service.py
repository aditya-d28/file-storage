import os
import time

from app.core.config import settings
from app.core.storage.storage_factory import StorageFactory
from app.entity.file_metadata import FileMetadata
from app.model.upload_model import FileDetailsModel
from app.repository.file_metadata_repository import (
    get_file_by_name_and_destination,
    insert,
    update,
)
from fastapi import UploadFile
from shared.logging.logger import get_logger
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


async def upload_file_to_storage(
    db: AsyncSession,
    name: str,
    file: UploadFile,
    destination: str = "",
    tags: str = "",
    description: str = "",
) -> FileDetailsModel:
    """
    Asynchronously uploads a file to the configured storage backend, manages file versioning, and updates or inserts file metadata in the database.

    Args:
        db (AsyncSession): The asynchronous database session for metadata operations.
        name (str): The original name of the file to be uploaded.
        file (UploadFile): The file object to be uploaded.
        destination (str, optional): The destination path within the storage bucket. Defaults to "".
        tags (str, optional): Comma-separated tags associated with the file. Defaults to "".
        description (str, optional): Description of the file. Defaults to "".

    Returns:
        FileDetailsModel: An object containing details about the uploaded file (name, size, destination, and update timestamp).

    Raises:
        Exception: If the file upload or metadata saving fails.
    """

    storage = StorageFactory.get_storage(
        settings.STORAGE_TYPE, settings.STORAGE_BUCKET_NAME
    )
    version = int(time.time())
    name_versioned = f"{os.path.splitext(name)[0]}_{version}{os.path.splitext(name)[1]}"
    destination = destination.strip("/")

    try:
        logger.info(f"Uploading file: {name_versioned} to {destination}")
        upload_details = await storage.upload(
            name=name_versioned, file=file, destination=destination
        )
        logger.info(f"File uploaded successfully: {name_versioned}")
    except Exception as err:
        logger.error(f"Error uploading file: {err}")
        raise Exception(f"Failed to upload file: {err}")

    try:
        file_metadata = await get_file_by_name_and_destination(
            db=db, file_name=name, destination=destination
        )
        if file_metadata:
            print(upload_details)
            file_metadata.file_path = upload_details.file_path
            file_metadata.version = version
            file_metadata.file_size = upload_details.file_size
            file_metadata.file_type = upload_details.file_type
            file_metadata.tags = tags
            file_metadata.description = description
            file_metadata = await update(db, file_metadata)
        else:
            file_metadata = FileMetadata(
                file_name=name,
                file_path=upload_details.file_path,
                file_size=upload_details.file_size,
                file_type=upload_details.file_type,
                destination=destination,
                version=version,
                user_id="system",
                description=description,
                tags=tags,
            )
            await insert(db, file_metadata)
        logger.info(f"File uploaded and metadata saved: {name}")
        return FileDetailsModel(
            file_name=name,
            file_size=upload_details.file_size,
            destination=destination,
            updated_at=file_metadata.updated_at.isoformat()
            if file_metadata.updated_at
            else file_metadata.created_at.isoformat(),
        )
    except Exception as err:
        logger.error(f"Error saving file metadata: {err}")
        await storage.delete(upload_details.file_path)
        raise Exception(f"Failed to save file metadata: {err}")
