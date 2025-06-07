from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.db_config import get_db
from app.core.logging.logger import get_logger
from app.model.enum import DeleteFileEnum
from app.service.delete_service import hard_delete_file, soft_delete_file

router = APIRouter()
logger = get_logger("system")


@router.delete("/file/{name}", summary="Deletes a file from the file-storage server.")
async def delete_file(
    name: str = Path(..., description="Name of the file to delete"),
    destination: str = Query("", description="Destination of the file"),
    delete_permanently: bool = Query(False, description="Delete file permanently"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Deletes a file either permanently or by soft deletion.
    Args:
        name (str): Name of the file to delete (from path parameter).
        destination (str, optional): Destination directory of the file (from query parameter). Defaults to "".
        delete_permanently (bool, optional): If True, deletes the file permanently; otherwise, performs a soft delete. Defaults to False.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: A message indicating the result of the deletion operation.

    Raises:
        HTTPException:
            - 404 if the file is not found.
            - 500 if there is an error during the deletion process.
    """

    destination = destination.strip("/")
    if delete_permanently:
        response = await hard_delete_file(db, file_name=name, destination=destination)
        if response == DeleteFileEnum.FILE_NOT_FOUND:
            logger.warning(f"File {name} not found.")
            raise HTTPException(status_code=404, detail=f"File {name} not found.")
        elif response == DeleteFileEnum.ERROR:
            logger.error(f"Error deleting file {name} permanently.")
            raise HTTPException(status_code=500, detail=f"Error deleting file {name} permanently.")
        logger.info(f"File {name} deleted permanently.")
        return {"message": f"File {name} deleted permanently."}
    else:
        response = await soft_delete_file(db, file_name=name, destination=destination)
        if response == DeleteFileEnum.FILE_NOT_FOUND:
            logger.warning(f"File {name} not found.")
            raise HTTPException(status_code=404, detail=f"File {name} not found.")
        elif response == DeleteFileEnum.ERROR:
            logger.error(f"Error deleting file {name}.")
            raise HTTPException(status_code=500, detail=f"Error deleting file {name}.")
        logger.info(f"File {name} deleted.")
        return {"message": f"File {name} deleted."}
