from app.entity.file_metadata import FileMetadata
from shared.logging.logger import get_logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

logger = get_logger(__name__)


async def insert(db: AsyncSession, file_metadata: FileMetadata) -> FileMetadata:
    """
    Inserts a new FileMetadata record into the database asynchronously.

    Args:
        db (AsyncSession): The asynchronous SQLAlchemy session to use for the operation.
        file_metadata (FileMetadata): The FileMetadata instance to be inserted.

    Returns:
        FileMetadata: The inserted FileMetadata instance with updated fields (e.g., primary key).

    Raises:
        SQLAlchemyError: If an error occurs during the database operation, the transaction is rolled back and the exception is re-raised.
    """

    try:
        db.add(file_metadata)
        await db.commit()
        await db.refresh(file_metadata)
        logger.debug(f"Inserted file metadata: {file_metadata.file_name}")
        return file_metadata
    except SQLAlchemyError as err:
        await db.rollback()
        logger.error(f"SQLAlchemyError: {err}")
        raise err


async def delete(db: AsyncSession, file_name: str) -> None:
    """
    Asynchronously deletes the file metadata entry with the specified file name from the database.

    Args:
        db (AsyncSession): The asynchronous database session to use for the operation.
        file_name (str): The name of the file whose metadata should be deleted.

    Raises:
        SQLAlchemyError: If a database error occurs during the deletion process.

    Logs:
        - Info: When the file metadata is successfully deleted.
        - Warning: If no file metadata is found for the given file name.
        - Error: If a SQLAlchemyError is encountered.
    """

    try:
        result = await db.execute(
            select(FileMetadata).where(FileMetadata.file_name == file_name)
        )
        file = result.scalar_one_or_none()
        if file:
            await db.delete(file)
            await db.commit()
            logger.debug(f"Deleted file metadata: {file_name}")
        else:
            logger.warning(f"File metadata not found for deletion: {file_name}")
    except SQLAlchemyError as err:
        await db.rollback()
        logger.error(f"SQLAlchemyError: {err}")
        raise err


async def get_file_by_name(db: AsyncSession, file_name: str) -> FileMetadata:
    """
    Asynchronously retrieves file metadata from the database by file name.

    Args:
        db (AsyncSession): The asynchronous database session.
        file_name (str): The name of the file to search for.

    Returns:
        List[FileMetadata]: A list of FileMetadata objects matching the file name and not marked as deleted.

    Raises:
        SQLAlchemyError: If a database error occurs during the query.
    """

    try:
        result = await db.execute(
            select(FileMetadata).where(
                FileMetadata.file_name == file_name,
                FileMetadata.is_deleted.is_(False),
            )
        )
        file_metadata = result.scalars().all()
        if file_metadata:
            logger.debug(f"Retrieved file metadata: {file_name}")
        else:
            logger.warning(f"File metadata not found: {file_name}")
        return file_metadata
    except SQLAlchemyError as err:
        logger.error(f"SQLAlchemyError: {err}")
        raise err


async def get_file_by_name_and_destination(
    db: AsyncSession, file_name: str, destination: str
) -> FileMetadata:
    """
    Asynchronously retrieves a FileMetadata record from the database by file name and destination.

    Args:
        db (AsyncSession): The asynchronous database session to use for the query.
        file_name (str): The name of the file to search for.
        destination (str): The destination associated with the file.

    Returns:
        FileMetadata or None: The FileMetadata object if found and not deleted, otherwise None.

    Raises:
        SQLAlchemyError: If a database error occurs during the query.
    """

    try:
        result = await db.execute(
            select(FileMetadata).where(
                FileMetadata.file_name == file_name,
                FileMetadata.destination == destination,
                FileMetadata.is_deleted.is_(False),
            )
        )
        file_metadata = result.scalar_one_or_none()
        if file_metadata:
            logger.debug(f"Retrieved file metadata: {file_metadata.file_name}")
        else:
            logger.warning(f"File metadata not found: {file_name} in {destination}")
        return file_metadata
    except SQLAlchemyError as err:
        logger.error(f"SQLAlchemyError: {err}")
        raise err


async def get_file_by_name_and_destination_for_hard_delete(
    db: AsyncSession, file_name: str, destination: str
) -> FileMetadata:
    """
    Retrieve a FileMetadata record by file name and destination for hard deletion.

    Args:
        db (AsyncSession): The asynchronous database session.
        file_name (str): The name of the file to retrieve.
        destination (str): The destination associated with the file.

    Returns:
        FileMetadata: The file metadata object if found, otherwise None.

    Raises:
        SQLAlchemyError: If a database error occurs during the query.
    """

    try:
        result = await db.execute(
            select(FileMetadata).where(
                FileMetadata.file_name == file_name,
                FileMetadata.destination == destination,
            )
        )
        file_metadata = result.scalar_one_or_none()
        if file_metadata:
            logger.debug(f"Retrieved file metadata: {file_metadata.file_name}")
        else:
            logger.warning(f"File metadata not found: {file_name} in {destination}")
        return file_metadata
    except SQLAlchemyError as err:
        logger.error(f"SQLAlchemyError: {err}")
        raise err


async def update(db: AsyncSession, file_metadata: FileMetadata) -> FileMetadata:
    """
    Asynchronously updates an existing FileMetadata record in the database.

    Args:
        db (AsyncSession): The asynchronous database session.
        file_metadata (FileMetadata): The FileMetadata instance to update.

    Returns:
        FileMetadata: The updated FileMetadata instance.

    Raises:
        SQLAlchemyError: If a database error occurs during the update process.

    Logs:
        - Info: When the file metadata is successfully updated.
        - Error: If a SQLAlchemyError is encountered.
    """

    try:
        await db.merge(file_metadata)
        await db.commit()
        await db.refresh(file_metadata)
        logger.debug(f"Updated file metadata: {file_metadata.file_name}")
        return file_metadata
    except SQLAlchemyError as err:
        await db.rollback()
        logger.error(f"SQLAlchemyError: {err}")
        raise err


async def get_list(
    db: AsyncSession,
    order_by_name: bool = False,
    order_by_size: bool = False,
    order_by_updated_at: bool = False,
    tag: str = None,
    destination: str = None,
) -> list[FileMetadata]:
    """
    Retrieve a list of non-deleted FileMetadata records from the database, with optional ordering and filtering.

    Args:
        db (AsyncSession): The asynchronous database session to use for the query.
        order_by_name (bool, optional): If True, order results by file name. Defaults to False.
        order_by_size (bool, optional): If True, order results by file size. Defaults to False.
        order_by_updated_at (bool, optional): If True, order results by updated timestamp (descending). Defaults to False.
        tag (str, optional): If provided, filter results to include only files containing this tag. Defaults to None.
        destination (str, optional): If provided, filter results to include only files in this destination or its subdirectories. Defaults to None.

    Returns:
        list[FileMetadata]: A list of FileMetadata objects matching the specified criteria.

    Raises:
        SQLAlchemyError: If a database error occurs during the query.
    """

    try:
        query = select(FileMetadata).where(FileMetadata.is_deleted.is_(False))
        if order_by_name:
            query = query.order_by(FileMetadata.file_name)
        elif order_by_size:
            query = query.order_by(FileMetadata.file_size)
        elif order_by_updated_at:
            query = query.order_by(FileMetadata.updated_at.desc())

        if tag:
            query = query.where(FileMetadata.tags.contains(tag))
        if destination:
            query = query.where(
                (FileMetadata.destination == destination)
                | (FileMetadata.destination.like(f"{destination}/%"))
            )

        result = await db.execute(query)
        logger.debug("Retrieved file metadata list.")
        return result.scalars().all()
    except SQLAlchemyError as err:
        logger.error(f"SQLAlchemyError: {err}")
        raise err
