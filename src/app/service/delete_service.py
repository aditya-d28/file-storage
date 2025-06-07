import os

from app.core.config import settings
from app.core.storage.storage_factory import StorageFactory
from app.model.enum import DeleteFileEnum
from app.repository.file_metadata_repository import (
    get_file_by_name_and_destination,
    get_file_by_name_and_destination_for_hard_delete,
    update,
)
from shared.logging.logger import get_logger
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


async def soft_delete_file(
    db: AsyncSession,
    file_name: str,
    destination: str,
) -> DeleteFileEnum:
    """
    Soft deletes a file by marking its metadata as deleted in the database.

    Args:
        db (AsyncSession): The asynchronous database session.
        file_name (str): The name of the file to be soft deleted.
        destination (str): The destination or location of the file.

    Returns:
        DeleteFileEnum: An enum indicating the result of the delete operation.
            - DeleteFileEnum.DELETED if the file was successfully soft deleted.
            - DeleteFileEnum.FILE_NOT_FOUND if the file does not exist.
            - DeleteFileEnum.ERROR if an error occurred during the operation.

    Logs:
        - Logs an error if the file is not found or if an exception occurs.
        - Logs an info message upon successful deletion.
    """

    try:
        file_metadata = await get_file_by_name_and_destination(
            db=db, file_name=file_name, destination=destination
        )
        if not file_metadata:
            logger.error(f"File {file_name} not found for soft delete.")
            return DeleteFileEnum.FILE_NOT_FOUND

        file_metadata.is_deleted = True
        await update(db, file_metadata)
        logger.info(f"File {file_name} deleted successfully.")
        return DeleteFileEnum.DELETED
    except Exception as err:
        logger.error(f"Error deleting file {file_name}: {err}")
        return DeleteFileEnum.ERROR


async def hard_delete_file(
    db: AsyncSession,
    file_name: str,
    destination: str,
) -> DeleteFileEnum:
    """
    Permanently deletes a file and its metadata from the database and storage.

    Args:
        db (AsyncSession): The asynchronous database session.
        file_name (str): The name of the file to be deleted.
        destination (str): The storage destination or path.

    Returns:
        DeleteFileEnum: An enum indicating the result of the delete operation.
            - FILE_NOT_FOUND: If the file metadata does not exist.
            - ERROR: If an error occurs during deletion.
            - DELETED: If the file and its metadata are successfully deleted.

    Raises:
        None. All exceptions are handled internally and logged.
    """

    try:
        storage = StorageFactory.get_storage(
            settings.STORAGE_TYPE, settings.STORAGE_BUCKET_NAME
        )
        file_metadata = await get_file_by_name_and_destination_for_hard_delete(
            db=db, file_name=file_name, destination=destination
        )
        if not file_metadata:
            logger.error(f"File {file_name} not found for delete.")
            return DeleteFileEnum.FILE_NOT_FOUND

        await db.delete(file_metadata)
        await db.commit()
    except Exception as err:
        logger.error(f"Error deleting file {file_name}: {err}")
        return DeleteFileEnum.ERROR

    try:
        name = f"{os.path.splitext(file_name)[0]}_{file_metadata.version}{os.path.splitext(file_name)[1]}"
        await storage.delete(name=name, destination=destination)
        logger.info(f"File {file_name} deleted permanently.")
    except Exception as err:
        logger.error(f"Error deleting file from storage {file_name}: {err}")

    return DeleteFileEnum.DELETED
