from typing import Optional

from app.core.database.db_config import get_db
from app.model.upload_model import FileDetailsModel
from app.service.upload_service import upload_file_to_storage
from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, UploadFile
from shared.logging.logger import get_logger
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
logger = get_logger("system")


@router.post("/file/{name}", summary="Uploads a file to the file-storage server.")
async def upload_file(
    name: str = Path(..., description="Name of the file to upload"),
    file: UploadFile = File(..., description="File to be uploaded"),
    destination: Optional[str] = Form("", description="Destination of the file"),
    tags: Optional[str] = Form("", description="Tags associated with the file"),
    description: Optional[str] = Form("", description="Description of the file"),
    db: AsyncSession = Depends(get_db),
) -> FileDetailsModel:
    """
    Uploads a file to the storage server with the specified metadata.

    Args:
        name (str): Name of the file to upload (from path parameter).
        file (UploadFile): The file to be uploaded.
        destination (str, optional): Destination directory for the file. Defaults to "".
        tags (str, optional): Tags to associate with the file. Defaults to "".
        description (str, optional): Description of the file. Defaults to "".
        db (AsyncSession): Database session (injected by FastAPI).

    Returns:
        FileDetailsModel: The details of the uploaded file upon successful upload.

    Raises:
        Exception: If an error occurs during the upload process, returns a dictionary with an "error" key containing the error message.
    """

    logger.info("Request received.")
    try:
        file_details = await upload_file_to_storage(
            db, name, file, destination=destination, tags=tags, description=description
        )
        logger.info("File uploaded successfully.")
        return file_details
    except Exception as err:
        logger.error(f"Error uploading file: {err}")
        raise HTTPException(status_code=500, detail=f"Error uploading file {name}.")
