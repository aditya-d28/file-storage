from unittest import mock

import pytest
from app.api.routes import list as list_route
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(list_route.router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def mock_get_file_list():
    with mock.patch("app.api.routes.list.get_file_list") as mocked:
        yield mocked


@pytest.fixture
def mock_get_db():
    async def _mock_db():
        yield mock.AsyncMock()

    return _mock_db


def test_list_files_success(client, mock_get_file_list, monkeypatch):
    # Mock return value with correct model fields
    mock_get_file_list.return_value = [
        {"fileName": "file1.txt", "fileSize": 1234, "destination": "test", "updatedAt": "2024-01-01T00:00:00Z"},
        {"fileName": "file2.txt", "fileSize": 5678, "destination": "test", "updatedAt": "2024-01-01T00:00:00Z"},
    ]

    # Patch get_db dependency to avoid DB access
    monkeypatch.setattr(list_route, "get_db", lambda: mock.AsyncMock())

    response = client.get("/files")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["fileName"] == "file1.txt"


def test_list_files_with_query_params(client, mock_get_file_list, monkeypatch):
    mock_get_file_list.return_value = [
        {"fileName": "fileA.txt", "fileSize": 1234, "destination": "docs", "updatedAt": "2024-01-01T00:00:00Z"}
    ]
    monkeypatch.setattr(list_route, "get_db", lambda: mock.AsyncMock())

    response = client.get("/files?order_by_name=true&destination=docs&tag=important&verbose=true")
    assert response.status_code == 200
    assert response.json()[0]["fileName"] == "fileA.txt"
    mock_get_file_list.assert_called_once()
    kwargs = mock_get_file_list.call_args.kwargs
    assert kwargs["order_by_name"] is True
    assert kwargs["destination"] == "docs"
    assert kwargs["tag"] == "important"
    assert kwargs["verbose"] is True


def test_list_files_error(client, mock_get_file_list, monkeypatch):
    mock_get_file_list.side_effect = Exception("DB error")
    monkeypatch.setattr(list_route, "get_db", lambda: mock.AsyncMock())

    response = client.get("/files")
    assert response.status_code == 500
    assert "detail" in response.json()
    assert response.json()["detail"] == "Error retrieving file list."
