import os
from unittest import mock

import pytest
from fastapi import UploadFile

from app.core.storage.file_storage import FileStorage
from app.model.upload_model import StorageUploadResponseModel


@pytest.fixture
def temp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def dummy_upload_file():
    mock_file = mock.AsyncMock()
    mock_file.read = mock.AsyncMock(return_value=b"test content")
    mock_file.content_type = "text/plain"
    mock_file.file_size = 12
    return mock_file


def test_init_creates_directory(tmp_path):
    dir_path = tmp_path / "bucket"
    assert not dir_path.exists()
    FileStorage(str(dir_path))
    assert dir_path.exists()


@pytest.mark.asyncio
async def test_upload_creates_file_and_returns_response(temp_dir, dummy_upload_file):
    storage = FileStorage(temp_dir)
    name = "test.txt"
    destination = "subdir"
    response = await storage.upload(name, dummy_upload_file, destination)
    expected_path = os.path.join(temp_dir, destination, name)
    assert os.path.exists(expected_path)
    assert isinstance(response, StorageUploadResponseModel)
    assert response.file_path == expected_path
    assert response.file_size == 12
    assert response.file_type == "text/plain"


@pytest.mark.asyncio
async def test_upload_sets_default_file_type_and_size(temp_dir):
    storage = FileStorage(temp_dir)
    name = "test2.txt"
    # Create a mock with the correct spec but without content_type and file_size
    dummy_file = mock.AsyncMock(spec=UploadFile)
    dummy_file.read = mock.AsyncMock(return_value=b"abc")
    # Remove content_type and file_size attributes to test fallback behavior
    delattr(dummy_file, "content_type")
    delattr(dummy_file, "file_size")
    response = await storage.upload(name, dummy_file)
    assert response.file_type == "application/octet-stream"
    assert response.file_size == 3


@pytest.mark.asyncio
async def test_upload_raises_exception_on_failure(temp_dir, dummy_upload_file):
    storage = FileStorage(temp_dir)
    with mock.patch("builtins.open", side_effect=OSError("fail")):
        with pytest.raises(Exception) as excinfo:
            await storage.upload("fail.txt", dummy_upload_file)
        assert "Failed to upload file to local storage" in str(excinfo.value)


@pytest.mark.asyncio
async def test_delete_removes_file(temp_dir):
    storage = FileStorage(temp_dir)
    name = "del.txt"
    destination = "del_dir"
    os.makedirs(os.path.join(temp_dir, destination))
    file_path = os.path.join(temp_dir, destination, name)
    with open(file_path, "wb") as f:
        f.write(b"delete me")
    assert os.path.exists(file_path)
    await storage.delete(name, destination)
    assert not os.path.exists(file_path)


@pytest.mark.asyncio
async def test_delete_raises_exception_on_failure(temp_dir):
    storage = FileStorage(temp_dir)
    with pytest.raises(Exception) as excinfo:
        await storage.delete("nonexistent.txt", "no_dir")
    assert "Failed to delete file from local storage" in str(excinfo.value)
