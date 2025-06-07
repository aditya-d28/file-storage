from app.model.file_storage_base_model import FileStorageBaseModel
from pydantic import Field


class StorageUploadResponseModel(FileStorageBaseModel):
    file_path: str = Field(..., description="The path where the file is stored")
    file_size: int = Field(..., description="The size of the uploaded file in bytes")
    file_type: str = Field(..., description="The MIME type of the uploaded file")


class FileDetailsModel(FileStorageBaseModel):
    file_name: str = Field(..., description="The name of the uploaded file")
    file_size: int = Field(..., description="The size of the uploaded file in bytes")
    destination: str = Field(..., description="The destination path where the file is stored")
    updated_at: str = Field(..., description="The last updated timestamp of the file metadata")


class FileDetailsVerboseModel(FileStorageBaseModel):
    file_name: str = Field(..., description="The name of the uploaded file")
    file_size: int = Field(..., description="The size of the uploaded file in bytes")
    file_type: str = Field(..., description="The MIME type of the uploaded file")
    file_path: str = Field(..., description="The path where the file is stored")
    destination: str = Field(..., description="The destination path where the file is stored")
    updated_at: str = Field(..., description="The last updated timestamp of the file metadata")
    tags: str = Field("", description="Tags associated with the file")
    description: str = Field("", description="Description of the file")
    version: int = Field(..., description="Version number of the file")
