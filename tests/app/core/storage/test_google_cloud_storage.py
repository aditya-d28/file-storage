from unittest.mock import MagicMock, patch

import pytest
from app.core.storage.google_cloud_storage import GoogleCloudStorage
from app.model.upload_model import StorageUploadResponseModel
from fastapi import UploadFile
from google.api_core.exceptions import NotFound


@pytest.fixture
def gcs_client_mock():
    with patch("google.cloud.storage.Client") as mock_client:
        mock_gcs = MagicMock()
        mock_client.return_value = mock_gcs

        # Mock bucket
        mock_bucket = MagicMock()
        mock_gcs.bucket.return_value = mock_bucket
        mock_gcs.get_bucket.return_value = mock_bucket
        mock_bucket.exists.return_value = True
        mock_bucket.name = "test-bucket"  # Set the bucket name property

        yield mock_gcs


@pytest.fixture
def gcs_storage(gcs_client_mock):
    return GoogleCloudStorage(bucket_name="test-bucket", location="us-central1")


@pytest.mark.asyncio
async def test_upload_file_success(gcs_storage, gcs_client_mock):
    # Arrange
    file_mock = MagicMock(spec=UploadFile)
    file_mock.file = MagicMock()
    file_mock.filename = "test.txt"
    file_mock.content_type = "text/plain"

    # Mock the blob
    mock_blob = MagicMock()
    gcs_client_mock.bucket.return_value.blob.return_value = mock_blob
    mock_blob.exists.return_value = False
    mock_blob.public_url = "https://storage.googleapis.com/test-bucket/test-folder/test.txt"
    mock_blob.content_type = "text/plain"
    mock_blob.size.return_value = 1234

    # Act
    result = await gcs_storage.upload("test.txt", file_mock, "test-folder")

    # Assert
    gcs_client_mock.bucket.return_value.blob.assert_called_once_with("test-folder/test.txt")
    assert isinstance(result, StorageUploadResponseModel)
    assert result.file_type == "text/plain"
    assert result.file_path == "gs://test-bucket/test-folder/test.txt"


@pytest.mark.asyncio
async def test_upload_file_error(gcs_storage, gcs_client_mock):
    # Arrange
    file_mock = MagicMock(spec=UploadFile)
    file_mock.file = MagicMock()

    # Mock the blob to raise an error
    mock_blob = MagicMock()
    gcs_client_mock.bucket.return_value.blob.return_value = mock_blob
    mock_blob.upload_from_file.side_effect = Exception("Upload failed")

    # Act & Assert
    with pytest.raises(Exception, match="Failed to upload file to Google Cloud Storage"):
        await gcs_storage.upload("test.txt", file_mock, "test-folder")


@pytest.mark.asyncio
async def test_delete_file_success(gcs_storage, gcs_client_mock):
    # Arrange
    mock_blob = MagicMock()
    # Get the bucket mock that was set up during initialization
    mock_bucket = gcs_client_mock.get_bucket.return_value
    mock_bucket.blob.return_value = mock_blob

    # Act
    await gcs_storage.delete("test.txt", "test-folder")

    # Assert
    mock_bucket.blob.assert_called_once_with("test-folder/test.txt")
    mock_blob.delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_file_error(gcs_storage, gcs_client_mock):
    # Arrange
    mock_blob = MagicMock()
    # Get the bucket mock that was set up during initialization
    mock_bucket = gcs_client_mock.get_bucket.return_value
    mock_bucket.blob.return_value = mock_blob
    mock_blob.delete.side_effect = Exception("Delete failed")

    # Act & Assert
    with pytest.raises(Exception, match="Failed to delete file from Google Cloud Storage"):
        await gcs_storage.delete("test.txt", "test-folder")


def test_init_bucket_exists(gcs_client_mock):
    # Act
    _ = GoogleCloudStorage(bucket_name="existing-bucket", location="us-central1")

    # Assert
    gcs_client_mock.get_bucket.assert_called_once_with("existing-bucket")
    gcs_client_mock.create_bucket.assert_not_called()


def test_init_create_bucket(gcs_client_mock):
    # Arrange
    gcs_client_mock.get_bucket.side_effect = NotFound("Bucket not found")

    # Act
    _ = GoogleCloudStorage(bucket_name="new-bucket", location="us-central1")

    # Assert
    gcs_client_mock.get_bucket.assert_called_once_with("new-bucket")
    gcs_client_mock.create_bucket.assert_called_once_with("new-bucket", location="us-central1")


def test_init_create_bucket_fails(gcs_client_mock):
    # Arrange
    gcs_client_mock.get_bucket.side_effect = NotFound("Bucket not found")
    gcs_client_mock.create_bucket.side_effect = Exception("Failed to create bucket")

    # Act & Assert
    with pytest.raises(Exception, match="Failed to create bucket 'failed-bucket'"):
        GoogleCloudStorage(bucket_name="failed-bucket", location="us-central1")

    gcs_client_mock.get_bucket.assert_called_once_with("failed-bucket")
    gcs_client_mock.create_bucket.assert_called_once_with("failed-bucket", location="us-central1")


def test_init_general_exception(gcs_client_mock):
    # Arrange
    gcs_client_mock.get_bucket.side_effect = Exception("General error")

    # Act & Assert
    with pytest.raises(Exception, match="Failed to create bucket 'error-bucket'"):
        GoogleCloudStorage(bucket_name="error-bucket", location="us-central1")

    gcs_client_mock.get_bucket.assert_called_once_with("error-bucket")
    gcs_client_mock.create_bucket.assert_not_called()
