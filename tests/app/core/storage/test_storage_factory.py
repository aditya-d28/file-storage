from unittest import mock

import pytest
from app.core.storage.storage_base import StorageBase
from app.core.storage.storage_factory import StorageFactory


@pytest.fixture
def mock_settings():
    with mock.patch("app.core.storage.storage_factory.settings") as settings_mock:
        settings_mock.S3_ENDPOINT_URL = "http://localhost:9000"
        settings_mock.STORAGE_AWS_ACCESS_KEY_ID = "test-access-key"
        settings_mock.STORAGE_AWS_SECRET_ACCESS_KEY = "test-secret-key"
        settings_mock.STORAGE_REGION_NAME = "us-test-1"
        settings_mock.STORAGE_GCS_LOCATION = "us-central1"
        yield settings_mock


@pytest.fixture
def mock_s3_storage():
    with mock.patch("app.core.storage.storage_factory.S3Storage") as s3_mock:
        s3_instance = mock.Mock(spec=StorageBase)
        s3_mock.return_value = s3_instance
        yield s3_mock


@pytest.fixture
def mock_gcs_storage():
    with mock.patch("app.core.storage.storage_factory.GoogleCloudStorage") as gcs_mock:
        gcs_instance = mock.Mock(spec=StorageBase)
        gcs_mock.return_value = gcs_instance
        yield gcs_mock


@pytest.fixture
def mock_file_storage():
    with mock.patch("app.core.storage.storage_factory.FileStorage") as file_mock:
        file_instance = mock.Mock(spec=StorageBase)
        file_instance.bucket_name = "testbucket"
        file_mock.return_value = file_instance
        yield file_mock, file_instance


def test_get_storage_local_returns_filestorage(mock_file_storage):
    mock_file_storage_class, mock_file_storage_instance = mock_file_storage
    storage = StorageFactory.get_storage("local", "testbucket")

    mock_file_storage_class.assert_called_once_with(bucket_name="testbucket")
    assert storage == mock_file_storage_instance
    assert isinstance(storage, StorageBase)  # Verify it implements base interface
    assert storage.bucket_name == "testbucket"


def test_get_storage_s3_returns_s3storage(mock_settings, mock_s3_storage):
    _ = StorageFactory.get_storage("s3", "testbucket")
    mock_s3_storage.assert_called_once_with(
        bucket_name="testbucket",
        endpoint_url="http://localhost:9000",
        aws_access_key_id="test-access-key",
        aws_secret_access_key="test-secret-key",
        region_name="us-test-1",
    )
    assert isinstance(mock_s3_storage.return_value, StorageBase)


def test_get_storage_gcs_returns_googlecloudstorage(mock_settings, mock_gcs_storage):
    _ = StorageFactory.get_storage("gcs", "testbucket")
    mock_gcs_storage.assert_called_once_with(bucket_name="testbucket", location="us-central1")
    assert isinstance(mock_gcs_storage.return_value, StorageBase)


def test_get_storage_invalid_type_raises_valueerror():
    with pytest.raises(ValueError) as excinfo:
        StorageFactory.get_storage("invalid", "testbucket")
    assert "Unknown storage type" in str(excinfo.value)
