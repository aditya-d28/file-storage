from app.model.upload_model import FileDetailsModel, FileDetailsVerboseModel
from app.repository.file_metadata_repository import get_list
from shared.logging.logger import get_logger

logger = get_logger(__name__)


async def get_file_list(
    db,
    order_by_name: bool = False,
    order_by_updated_at: bool = False,
    order_by_size: bool = False,
    destination: str = "",
    tag: str = "",
    verbose: bool = False,
) -> list[FileDetailsModel] | list[FileDetailsVerboseModel]:
    """
    Retrieve a list of files from the database with optional ordering, filtering, and verbosity.
    Args:
        db: Database session or connection object.
        order_by_name (bool, optional): If True, order the files by name. Defaults to False.
        order_by_updated_at (bool, optional): If True, order the files by last updated timestamp. Defaults to False.
        order_by_size (bool, optional): If True, order the files by size. Defaults to False.
        destination (str, optional): Filter files by destination. Defaults to "" (no filter).
        tag (str, optional): Filter files by tag. Defaults to "" (no filter).
        verbose (bool, optional): If True, return detailed file information. Defaults to False.
    Returns:
        list[FileDetailsModel] | list[FileDetailsVerboseModel]:
            A list of file details, either in basic or verbose format depending on the `verbose` flag.
    Raises:
        Exception: If an error occurs while retrieving the file list.
    """

    try:
        files = await get_list(
            db=db,
            order_by_name=order_by_name,
            order_by_updated_at=order_by_updated_at,
            order_by_size=order_by_size,
            destination=destination,
            tag=tag,
        )
        logger.debug(f"Retrieved {len(files)} files from the database.")

        if verbose:
            response = [
                FileDetailsVerboseModel(
                    file_name=str(file.file_name),
                    file_path=str(file.file_path),
                    file_size=int(file.file_size),
                    file_type=str(file.file_type),
                    destination=str(file.destination or ""),
                    updated_at=(
                        file.updated_at.isoformat()
                        if getattr(file, "updated_at", None)
                        else file.created_at.isoformat()
                    ),
                    version=int(file.version),
                    tags=str(file.tags),
                    description=str(file.description),
                )
                for file in files
            ]
        else:
            response = [
                FileDetailsModel(
                    file_name=str(file.file_name),
                    file_size=int(file.file_size),
                    destination=str(file.destination or ""),
                    updated_at=(
                        file.updated_at.isoformat()
                        if getattr(file, "updated_at", None)
                        else file.created_at.isoformat()
                    ),
                )
                for file in files
            ]

        return response
    except Exception as err:
        logger.error(f"Error listing files: {err}")
        raise Exception(f"Error listing files: {err}")
