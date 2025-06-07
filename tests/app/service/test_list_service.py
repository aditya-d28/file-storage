from datetime import datetime
from unittest import mock

import pytest

import app.service.list_service as list_service


@pytest.fixture
def fake_file_basic():
    class FakeFile:
        file_name = "test.txt"
        file_path = "/files/test.txt"
        file_size = 123
        file_type = "text/plain"
        destination = "bucket1"
        updated_at = datetime(2024, 1, 1, 12, 0, 0)
        created_at = datetime(2023, 12, 31, 12, 0, 0)
        version = 1
        tags = "tag1,tag2"
        description = "desc"

    return FakeFile()


@pytest.fixture
def fake_file_no_updated():
    class FakeFile:
        file_name = "test2.txt"
        file_path = "/files/test2.txt"
        file_size = 456
        file_type = "text/plain"
        destination = "bucket2"
        updated_at = None
        created_at = datetime(2023, 12, 30, 12, 0, 0)
        version = 2
        tags = "tag3"
        description = "desc2"

    return FakeFile()


@pytest.mark.asyncio
async def test_get_file_list_basic(monkeypatch, fake_file_basic):
    mock_db = mock.Mock()
    files = [fake_file_basic]
    monkeypatch.setattr(list_service, "get_list", mock.AsyncMock(return_value=files))
    # Patch logger to avoid side effects
    monkeypatch.setattr(list_service.logger, "debug", lambda msg: None)

    result = await list_service.get_file_list(mock_db)
    assert isinstance(result, list)
    assert len(result) == 1
    file = result[0]
    assert file.file_name == "test.txt"
    assert file.file_size == 123
    assert file.destination == "bucket1"
    assert file.updated_at == fake_file_basic.updated_at.isoformat()


@pytest.mark.asyncio
async def test_get_file_list_verbose(monkeypatch, fake_file_basic):
    mock_db = mock.Mock()
    files = [fake_file_basic]
    monkeypatch.setattr(list_service, "get_list", mock.AsyncMock(return_value=files))
    monkeypatch.setattr(list_service.logger, "debug", lambda msg: None)

    result = await list_service.get_file_list(mock_db, verbose=True)
    assert isinstance(result, list)
    assert len(result) == 1
    file = result[0]
    assert file.file_name == "test.txt"
    assert file.file_path == "/files/test.txt"
    assert file.file_size == 123
    assert file.file_type == "text/plain"
    assert file.destination == "bucket1"
    assert file.updated_at == fake_file_basic.updated_at.isoformat()
    assert file.version == 1
    assert file.tags == "tag1,tag2"
    assert file.description == "desc"


@pytest.mark.asyncio
async def test_get_file_list_no_updated(monkeypatch, fake_file_no_updated):
    mock_db = mock.Mock()
    files = [fake_file_no_updated]
    monkeypatch.setattr(list_service, "get_list", mock.AsyncMock(return_value=files))
    monkeypatch.setattr(list_service.logger, "debug", lambda msg: None)

    result = await list_service.get_file_list(mock_db)
    assert result[0].updated_at == fake_file_no_updated.created_at.isoformat()


@pytest.mark.asyncio
async def test_get_file_list_with_filters(monkeypatch, fake_file_basic):
    mock_db = mock.Mock()
    files = [fake_file_basic]
    get_list_mock = mock.AsyncMock(return_value=files)
    monkeypatch.setattr(list_service, "get_list", get_list_mock)
    monkeypatch.setattr(list_service.logger, "debug", lambda msg: None)

    await list_service.get_file_list(
        mock_db,
        order_by_name=True,
        order_by_updated_at=True,
        order_by_size=True,
        destination="bucket1",
        tag="tag1",
    )
    get_list_mock.assert_awaited_once_with(
        db=mock_db,
        order_by_name=True,
        order_by_updated_at=True,
        order_by_size=True,
        destination="bucket1",
        tag="tag1",
    )


@pytest.mark.asyncio
async def test_get_file_list_exception(monkeypatch):
    mock_db = mock.Mock()
    monkeypatch.setattr(list_service, "get_list", mock.AsyncMock(side_effect=Exception("db error")))
    monkeypatch.setattr(list_service.logger, "error", lambda msg: None)

    with pytest.raises(Exception) as excinfo:
        await list_service.get_file_list(mock_db)
    assert "Error listing files: db error" in str(excinfo.value)
