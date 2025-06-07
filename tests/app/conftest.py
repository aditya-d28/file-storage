import sys
from unittest import mock
import pytest


@pytest.fixture(autouse=True, scope="session")
def patch_settings_and_db():
    mock_settings = mock.MagicMock()
    mock_settings.API_VER_STR = "/v1"
    mock_settings.PROJECT_NAME = "TestProject"
    mock_settings.CONSOLE_LOG_LEVEL = "INFO"
    mock_settings.FILE_LOG_LEVEL = "INFO"
    mock_settings.DEV_MODE = "Y"
    mock_settings.DB_TYPE = "sqlite"
    mock_settings.DB_HOST = "localhost"
    mock_settings.DB_PORT = "5432"
    mock_settings.DB_NAME = "test_db"
    mock_settings.DB_USER = "user"
    mock_settings.DB_PASSWORD = "pass"
    mock_settings.DB_POOL_SIZE = 5
    mock_settings.DB_MAX_OVERFLOW = 10
    mock_settings.STORAGE_TYPE = "local"
    mock_settings.STORAGE_BUCKET_NAME = "bucket"
    mock_settings.S3_ENDPOINT_URL = "http://test-endpoint.com"
    mock_settings.STORAGE_AWS_ACCESS_KEY_ID = "user123"
    mock_settings.STORAGE_AWS_SECRET_ACCESS_KEY = "password123"
    mock_settings.STORAGE_REGION_NAME = "mock-region-1"
    mock_settings.STORAGE_GCS_LOCATION = "mock-location1"
    mock_settings.ALLOWED_ORIGINS = ["*"]
    mock_settings.DB_URL = "sqlite+aiosqlite:///test_db.sqlite3"
    mock_settings.ALLOWED_ORIGINS_LIST = ["*"]

    mock_config_module = mock.MagicMock(settings=mock_settings)
    sys.modules["app.core.config"] = mock_config_module

    mock_get_db = mock.MagicMock()
    sys.modules["app.core.database.db_config"] = mock.MagicMock(get_db=mock_get_db)
    yield
