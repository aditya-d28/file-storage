from unittest.mock import MagicMock, patch

import pytest
from app.core.storage.s3_storage import S3Storage
from app.model.upload_model import StorageUploadResponseModel
from botocore.exceptions import ClientError
from fastapi import UploadFile


@pytest.fixture
def s3_client_mock():
    with patch("boto3.client") as mock_client:
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        mock_s3.head_bucket.return_value = True  # Bucket exists
        yield mock_s3


@pytest.fixture
def s3_storage(s3_client_mock):
    return S3Storage(
        bucket_name="test-bucket",
        endpoint_url="http://localhost:9000",
        aws_access_key_id="test-key",
        aws_secret_access_key="test-secret",
        region_name="us-east-1",
    )


@pytest.mark.asyncio
async def test_upload_file_success(s3_storage, s3_client_mock):
    # Arrange
    file_mock = MagicMock(spec=UploadFile)
    file_mock.file = MagicMock()
    file_mock.filename = "test.txt"

    s3_client_mock.head_object.return_value = {
        "ContentLength": 1234,
        "ContentType": "text/plain",
    }

    # Act
    result = await s3_storage.upload("test.txt", file_mock, "test-folder")

    # Assert
    s3_client_mock.upload_fileobj.assert_called_once_with(file_mock.file, "test-bucket", "test-folder/test.txt")
    s3_client_mock.head_object.assert_called_once_with(Bucket="test-bucket", Key="test-folder/test.txt")
    assert isinstance(result, StorageUploadResponseModel)
    assert result.file_size == 1234
    assert result.file_type == "text/plain"
    assert result.file_path == "s3://test-bucket/test-folder/test.txt"


@pytest.mark.asyncio
async def test_upload_file_client_error(s3_storage, s3_client_mock):
    # Arrange
    file_mock = MagicMock(spec=UploadFile)
    file_mock.file = MagicMock()
    s3_client_mock.upload_fileobj.side_effect = ClientError(
        error_response={"Error": {"Message": "Upload failed"}},
        operation_name="upload_fileobj",
    )

    # Act & Assert
    with pytest.raises(Exception, match="Failed to upload file to S3"):
        await s3_storage.upload("test.txt", file_mock, "test-folder")


@pytest.mark.asyncio
async def test_delete_file_success(s3_storage, s3_client_mock):
    # Act
    await s3_storage.delete("test.txt", "test-folder")

    # Assert
    s3_client_mock.delete_object.assert_called_once_with(Bucket="test-bucket", Key="test-folder/test.txt")


@pytest.mark.asyncio
async def test_delete_file_client_error(s3_storage, s3_client_mock):
    # Arrange
    s3_client_mock.delete_object.side_effect = ClientError(
        error_response={"Error": {"Message": "Delete failed"}},
        operation_name="delete_object",
    )

    # Act & Assert
    with pytest.raises(Exception, match="Failed to delete file from S3"):
        await s3_storage.delete("test.txt", "test-folder")


def test_init_bucket_exists(s3_client_mock):
    # Arrange & Act
    S3Storage(
        bucket_name="existing-bucket",
        endpoint_url="http://localhost:9000",
        aws_access_key_id="test-key",
        aws_secret_access_key="test-secret",
        region_name="us-east-1",
    )

    # Assert
    s3_client_mock.head_bucket.assert_called_once_with(Bucket="existing-bucket")
    s3_client_mock.create_bucket.assert_not_called()


def test_init_create_bucket(s3_client_mock):
    # Arrange
    s3_client_mock.head_bucket.side_effect = ClientError(
        error_response={"Error": {"Message": "Bucket does not exist"}},
        operation_name="head_bucket",
    )

    # Act
    S3Storage(
        bucket_name="new-bucket",
        endpoint_url="http://localhost:9000",
        aws_access_key_id="test-key",
        aws_secret_access_key="test-secret",
        region_name="us-east-1",
    )

    # Assert
    s3_client_mock.head_bucket.assert_called_once_with(Bucket="new-bucket")
    s3_client_mock.create_bucket.assert_called_once_with(
        Bucket="new-bucket",
        CreateBucketConfiguration={"LocationConstraint": "us-east-1"},
    )


def test_init_create_bucket_fails(s3_client_mock):
    # Arrange
    s3_client_mock.head_bucket.side_effect = ClientError(
        error_response={"Error": {"Message": "Bucket does not exist"}},
        operation_name="head_bucket",
    )
    s3_client_mock.create_bucket.side_effect = ClientError(
        error_response={"Error": {"Message": "Failed to create bucket"}},
        operation_name="create_bucket",
    )

    # Act & Assert
    with pytest.raises(Exception, match="Failed to create bucket"):
        S3Storage(
            bucket_name="failed-bucket",
            endpoint_url="http://localhost:9000",
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret",
            region_name="us-east-1",
        )

    s3_client_mock.head_bucket.assert_called_once_with(Bucket="failed-bucket")
    s3_client_mock.create_bucket.assert_called_once_with(
        Bucket="failed-bucket",
        CreateBucketConfiguration={"LocationConstraint": "us-east-1"},
    )


def test_init_general_exception(s3_client_mock):
    # Arrange
    s3_client_mock.head_bucket.side_effect = Exception("General error")

    # Act & Assert
    with pytest.raises(Exception, match="General error"):
        S3Storage(
            bucket_name="error-bucket",
            endpoint_url="http://localhost:9000",
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret",
            region_name="us-east-1",
        )

    s3_client_mock.head_bucket.assert_called_once_with(Bucket="error-bucket")
    s3_client_mock.create_bucket.assert_not_called()
