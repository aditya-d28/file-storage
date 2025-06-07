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
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.routes.upload import router
from app.model.upload_model import FileDetailsModel

app = FastAPI()
app.include_router(router)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def file_details_model():
    return FileDetailsModel(
        file_name="test.txt",
        file_size=1234,
        destination="",
        updated_at="2024-01-01T00:00:00Z",
    )


@patch("app.api.routes.upload.upload_file_to_storage", new_callable=AsyncMock)
@patch("app.api.routes.upload.get_db")
def test_upload_file_success(mock_get_db, mock_upload_file_to_storage, client, file_details_model, mock_db):
    mock_get_db.return_value = mock_db
    mock_upload_file_to_storage.return_value = file_details_model

    with open(__file__, "rb") as f:
        response = client.post(
            "/file/test.txt",
            files={"file": ("test.txt", f, "text/plain")},
            data={
                "destination": "folder",
                "tags": "tag1,tag2",
                "description": "A test file",
            },
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["fileName"] == "test.txt"


@patch("app.api.routes.upload.upload_file_to_storage", new_callable=AsyncMock)
@patch("app.api.routes.upload.get_db")
def test_upload_file_error(mock_get_db, mock_upload_file_to_storage, client, mock_db):
    mock_get_db.return_value = mock_db
    mock_upload_file_to_storage.side_effect = Exception("Upload failed")

    with open(__file__, "rb") as f:
        response = client.post(
            "/file/test.txt",
            files={"file": ("test.txt", f, "text/plain")},
            data={"destination": "", "tags": "", "description": ""},
        )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "detail" in response.json()
    assert "Error uploading file" in response.json()["detail"]
