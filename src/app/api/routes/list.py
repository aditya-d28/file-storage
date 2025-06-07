from app.core.database.db_config import get_db
from app.model.upload_model import FileDetailsModel, FileDetailsVerboseModel
from app.service.list_service import get_file_list
from fastapi import APIRouter, Depends, HTTPException, Query
from shared.logging.logger import get_logger
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
logger = get_logger(__name__)


@router.get("/files", summary="Lists all files in the file-storage server.")
async def list_files(
    order_by_name: bool = Query(False, description="Sort files by name (a -> z)"),
    order_by_updated_at: bool = Query(False, description="Sort files by date (recently updated first)"),
    order_by_size: bool = Query(False, description="Sort files by size (smallest first)"),
    destination: str = Query("", description="Directory to list files from"),
    tag: str = Query("", description="Filter files by tag"),
    verbose: bool = Query(False, description="Include version information"),
    db: AsyncSession = Depends(get_db),
) -> list[FileDetailsModel] | list[FileDetailsVerboseModel]:
    """
    Lists all files in the storage server, with optional filtering and sorting.

    Args:
        order_by_name (bool): Sort files by name if True (a -> z).
        order_by_updated_at (bool): Sort files by last update date if True (recently updated first).
        order_by_size (bool): Sort files by size if True (smallest first).
        destination (str): Filter files by destination directory.
        tag (str): Filter files by tag.
        verbose (bool): Include additional version information if True.
        db (AsyncSession): Database session (injected by FastAPI).

    Returns:
        Union[List[FileDetailsModel], List[FileDetailsVerboseModel], Dict]: List of file details or error message.

    Raises:
        Exception: If an error occurs while retrieving the file list.
    """

    logger.info("Request received to list files.")
    destination = destination.strip("/")

    try:
        files = await get_file_list(
            db=db,
            order_by_name=order_by_name,
            order_by_updated_at=order_by_updated_at,
            order_by_size=order_by_size,
            destination=destination,
            tag=tag,
            verbose=verbose,
        )
        logger.info("File list retrieved successfully.")
        return files
    except Exception as err:
        logger.error(f"Error retrieving file list: {err}")
        raise HTTPException(status_code=500, detail="Error retrieving file list.")
