import os

# Set required environment variables before any app imports
os.environ["PROJECT_NAME"] = "test_project"
os.environ["CONSOLE_LOG_LEVEL"] = "INFO"
os.environ["FILE_LOG_LEVEL"] = "INFO"
os.environ["DEV_MODE"] = "True"
os.environ["DB_TYPE"] = "sqlite"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "test_db"
os.environ["DB_USER"] = "user"
os.environ["DB_PASSWORD"] = "password"
os.environ["DB_POOL_SIZE"] = "5"
os.environ["DB_MAX_OVERFLOW"] = "10"
os.environ["STORAGE_TYPE"] = "mock"
os.environ["STORAGE_BUCKET_NAME"] = "bucket"

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.model.upload_model import FileDetailsModel
from app.service.upload_service import upload_file_to_storage


@pytest.mark.asyncio
@patch("app.service.upload_service.StorageFactory.get_storage")
@patch("app.service.upload_service.get_file_by_name_and_destination")
@patch("app.service.upload_service.insert")
@patch("app.service.upload_service.update")
@patch("app.service.upload_service.FileMetadata")
@patch("app.service.upload_service.settings")
@patch("app.service.upload_service.logger")
@patch("time.time", return_value=1234567890)
async def test_upload_file_to_storage_insert(
    mock_time,
    mock_logger,
    mock_settings,
    mock_FileMetadata,
    mock_update,
    mock_insert,
    mock_get_file_by_name_and_destination,
    mock_get_storage,
    monkeypatch,
):
    # Arrange
    mock_settings.STORAGE_TYPE = "mock"
    mock_settings.STORAGE_BUCKET_NAME = "bucket"
    mock_storage = AsyncMock()
    mock_get_storage.return_value = mock_storage

    # Mock upload details
    upload_details = MagicMock()
    upload_details.file_path = "path/to/file"
    upload_details.file_size = 1234
    upload_details.file_type = "text/plain"
    mock_storage.upload.return_value = upload_details

    # No existing metadata
    mock_get_file_by_name_and_destination.return_value = None

    # Mock FileMetadata instance
    file_metadata_instance = MagicMock()
    file_metadata_instance.updated_at = None
    file_metadata_instance.created_at.isoformat.return_value = "2024-01-01T00:00:00"
    mock_FileMetadata.return_value = file_metadata_instance

    db = MagicMock()
    file = MagicMock()
    name = "test.txt"
    destination = "folder"
    tags = "tag1,tag2"
    description = "desc"

    # Act
    result = await upload_file_to_storage(db, name, file, destination, tags, description)

    # Assert
    mock_get_storage.assert_called_once_with("mock", "bucket")
    mock_storage.upload.assert_awaited_once()
    mock_get_file_by_name_and_destination.assert_awaited_once()
    mock_insert.assert_awaited_once_with(db, file_metadata_instance)
    assert isinstance(result, FileDetailsModel)
    assert result.file_name == name
    assert result.file_size == upload_details.file_size
    assert result.destination == destination
    assert result.updated_at == "2024-01-01T00:00:00"


@pytest.mark.asyncio
@patch("app.service.upload_service.StorageFactory.get_storage")
@patch("app.service.upload_service.get_file_by_name_and_destination")
@patch("app.service.upload_service.insert")
@patch("app.service.upload_service.update")
@patch("app.service.upload_service.FileMetadata")
@patch("app.service.upload_service.settings")
@patch("app.service.upload_service.logger")
@patch("time.time", return_value=1234567890)
async def test_upload_file_to_storage_update(
    mock_time,
    mock_logger,
    mock_settings,
    mock_FileMetadata,
    mock_update,
    mock_insert,
    mock_get_file_by_name_and_destination,
    mock_get_storage,
    monkeypatch,
):
    # Arrange
    mock_settings.STORAGE_TYPE = "mock"
    mock_settings.STORAGE_BUCKET_NAME = "bucket"
    mock_storage = AsyncMock()
    mock_get_storage.return_value = mock_storage

    upload_details = MagicMock()
    upload_details.file_path = "path/to/file"
    upload_details.file_size = 1234
    upload_details.file_type = "text/plain"
    mock_storage.upload.return_value = upload_details

    # Existing metadata
    file_metadata_instance = MagicMock()
    file_metadata_instance.updated_at.isoformat.return_value = "2024-01-02T00:00:00"
    file_metadata_instance.created_at = None
    mock_get_file_by_name_and_destination.return_value = file_metadata_instance

    mock_update.return_value = file_metadata_instance

    db = MagicMock()
    file = MagicMock()
    name = "test.txt"
    destination = "folder"
    tags = "tag1,tag2"
    description = "desc"

    # Act
    result = await upload_file_to_storage(db, name, file, destination, tags, description)

    # Assert
    mock_get_storage.assert_called_once_with("mock", "bucket")
    mock_storage.upload.assert_awaited_once()
    mock_get_file_by_name_and_destination.assert_awaited_once()
    mock_update.assert_awaited_once_with(db, file_metadata_instance)
    assert isinstance(result, FileDetailsModel)
    assert result.file_name == name
    assert result.file_size == upload_details.file_size
    assert result.destination == destination
    assert result.updated_at == "2024-01-02T00:00:00"


@pytest.mark.asyncio
@patch("app.service.upload_service.StorageFactory.get_storage")
@patch("app.service.upload_service.logger")
@patch("app.service.upload_service.settings")
@patch("time.time", return_value=1234567890)
async def test_upload_file_to_storage_upload_exception(
    mock_time, mock_settings, mock_logger, mock_get_storage, monkeypatch
):
    # Arrange
    mock_settings.STORAGE_TYPE = "mock"
    mock_settings.STORAGE_BUCKET_NAME = "bucket"
    mock_storage = AsyncMock()
    mock_get_storage.return_value = mock_storage
    mock_storage.upload.side_effect = Exception("upload failed")

    db = MagicMock()
    file = MagicMock()
    name = "test.txt"
    destination = "folder"

    # Act & Assert
    with pytest.raises(Exception, match="Failed to upload file: upload failed"):
        await upload_file_to_storage(db, name, file, destination)


@pytest.mark.asyncio
@patch("app.service.upload_service.StorageFactory.get_storage")
@patch("app.service.upload_service.get_file_by_name_and_destination")
@patch("app.service.upload_service.insert")
@patch("app.service.upload_service.update")
@patch("app.service.upload_service.FileMetadata")
@patch("app.service.upload_service.settings")
@patch("app.service.upload_service.logger")
@patch("time.time", return_value=1234567890)
async def test_upload_file_to_storage_metadata_exception(
    mock_time,
    mock_logger,
    mock_settings,
    mock_FileMetadata,
    mock_update,
    mock_insert,
    mock_get_file_by_name_and_destination,
    mock_get_storage,
    monkeypatch,
):
    # Arrange
    mock_settings.STORAGE_TYPE = "mock"
    mock_settings.STORAGE_BUCKET_NAME = "bucket"
    mock_storage = AsyncMock()
    mock_get_storage.return_value = mock_storage

    upload_details = MagicMock()
    upload_details.file_path = "path/to/file"
    upload_details.file_size = 1234
    upload_details.file_type = "text/plain"
    mock_storage.upload.return_value = upload_details

    mock_get_file_by_name_and_destination.side_effect = Exception("db error")
    mock_storage.delete = AsyncMock()

    db = MagicMock()
    file = MagicMock()
    name = "test.txt"
    destination = "folder"

    # Act & Assert
    with pytest.raises(Exception, match="Failed to save file metadata: db error"):
        await upload_file_to_storage(db, name, file, destination)
    mock_storage.delete.assert_awaited_once()
