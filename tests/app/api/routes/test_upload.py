import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.api.routes.upload import router
from app.model.upload_model import FileDetailsModel
from fastapi import FastAPI

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
def test_upload_file_success(
    mock_get_db, mock_upload_file_to_storage, client, file_details_model, mock_db
):
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

    assert response.status_code == status.HTTP_200_OK
    assert "error" in response.json()
    assert response.json()["error"] == "Upload failed"
