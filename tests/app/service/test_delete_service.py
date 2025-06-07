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

import app.service.delete_service as delete_service
from app.model.enum import DeleteFileEnum


@pytest.mark.asyncio
@patch("app.service.delete_service.StorageFactory")
@patch(
    "app.service.delete_service.get_file_by_name_and_destination_for_hard_delete",
    new_callable=AsyncMock,
)
async def test_hard_delete_file_success(mock_get_file, mock_storage_factory):
    # Arrange
    db = AsyncMock()
    file_name = "test.txt"
    destination = "folder"
    file_metadata = MagicMock()
    file_metadata.version = 2
    mock_get_file.return_value = file_metadata

    mock_storage = AsyncMock()
    mock_storage_factory.get_storage.return_value = mock_storage

    # Act
    result = await delete_service.hard_delete_file(db, file_name, destination)

    # Assert
    mock_get_file.assert_awaited_once_with(db=db, file_name=file_name, destination=destination)
    db.delete.assert_awaited_once_with(file_metadata)
    db.commit.assert_awaited_once()
    mock_storage.delete.assert_awaited_once_with(name="test_2.txt", destination=destination)
    assert result == DeleteFileEnum.DELETED


@pytest.mark.asyncio
@patch("app.service.delete_service.StorageFactory")
@patch(
    "app.service.delete_service.get_file_by_name_and_destination_for_hard_delete",
    new_callable=AsyncMock,
)
async def test_hard_delete_file_file_not_found(mock_get_file, mock_storage_factory):
    db = AsyncMock()
    file_name = "missing.txt"
    destination = "folder"
    mock_get_file.return_value = None

    result = await delete_service.hard_delete_file(db, file_name, destination)

    assert result == DeleteFileEnum.FILE_NOT_FOUND
    db.delete.assert_not_called()
    db.commit.assert_not_called()
    mock_storage_factory.get_storage.assert_called_once()


@pytest.mark.asyncio
@patch("app.service.delete_service.StorageFactory")
@patch(
    "app.service.delete_service.get_file_by_name_and_destination_for_hard_delete",
    new_callable=AsyncMock,
)
async def test_hard_delete_file_db_exception(mock_get_file, mock_storage_factory):
    db = AsyncMock()
    file_name = "test.txt"
    destination = "folder"
    file_metadata = MagicMock()
    file_metadata.version = 1
    mock_get_file.return_value = file_metadata

    db.delete.side_effect = Exception("DB error")
    mock_storage_factory.get_storage.return_value = AsyncMock()

    result = await delete_service.hard_delete_file(db, file_name, destination)

    assert result == DeleteFileEnum.ERROR


@pytest.mark.asyncio
@patch("app.service.delete_service.StorageFactory")
@patch(
    "app.service.delete_service.get_file_by_name_and_destination_for_hard_delete",
    new_callable=AsyncMock,
)
async def test_hard_delete_file_storage_exception(mock_get_file, mock_storage_factory):
    db = AsyncMock()
    file_name = "test.txt"
    destination = "folder"
    file_metadata = MagicMock()
    file_metadata.version = 3
    mock_get_file.return_value = file_metadata

    mock_storage = AsyncMock()
    mock_storage.delete.side_effect = Exception("Storage error")
    mock_storage_factory.get_storage.return_value = mock_storage

    # db.delete and db.commit should work
    result = await delete_service.hard_delete_file(db, file_name, destination)

    # Should still return DELETED even if storage deletion fails
    assert result == DeleteFileEnum.DELETED
    mock_storage.delete.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.service.delete_service.get_file_by_name_and_destination", new_callable=AsyncMock)
@patch("app.service.delete_service.update", new_callable=AsyncMock)
async def test_soft_delete_file_success(mock_update, mock_get_file):
    # Arrange
    db = AsyncMock()
    file_name = "test.txt"
    destination = "folder"
    file_metadata = MagicMock()
    mock_get_file.return_value = file_metadata

    # Act
    result = await delete_service.soft_delete_file(db, file_name, destination)

    # Assert
    mock_get_file.assert_awaited_once_with(db=db, file_name=file_name, destination=destination)
    assert file_metadata.is_deleted is True
    mock_update.assert_awaited_once_with(db, file_metadata)
    assert result == DeleteFileEnum.DELETED


@pytest.mark.asyncio
@patch("app.service.delete_service.get_file_by_name_and_destination", new_callable=AsyncMock)
async def test_soft_delete_file_not_found(mock_get_file):
    # Arrange
    db = AsyncMock()
    file_name = "missing.txt"
    destination = "folder"
    mock_get_file.return_value = None

    # Act
    result = await delete_service.soft_delete_file(db, file_name, destination)

    # Assert
    assert result == DeleteFileEnum.FILE_NOT_FOUND
    mock_get_file.assert_awaited_once_with(db=db, file_name=file_name, destination=destination)


@pytest.mark.asyncio
@patch("app.service.delete_service.get_file_by_name_and_destination", new_callable=AsyncMock)
@patch("app.service.delete_service.update", new_callable=AsyncMock)
async def test_soft_delete_file_db_exception(mock_update, mock_get_file):
    # Arrange
    db = AsyncMock()
    file_name = "test.txt"
    destination = "folder"
    file_metadata = MagicMock()
    mock_get_file.return_value = file_metadata
    mock_update.side_effect = Exception("DB error")

    # Act
    result = await delete_service.soft_delete_file(db, file_name, destination)

    # Assert
    assert result == DeleteFileEnum.ERROR
    mock_get_file.assert_awaited_once_with(db=db, file_name=file_name, destination=destination)
    assert file_metadata.is_deleted is True
    mock_update.assert_awaited_once_with(db, file_metadata)
