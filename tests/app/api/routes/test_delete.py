from unittest import mock

import pytest
from fastapi import HTTPException, status

from app.api.routes.delete import delete_file
from app.model.enum import DeleteFileEnum


@pytest.mark.asyncio
@mock.patch("app.api.routes.delete.hard_delete_file")
@mock.patch("app.api.routes.delete.soft_delete_file")
@mock.patch("app.api.routes.delete.logger")
async def test_delete_file_soft_success(mock_logger, mock_soft_delete_file, mock_hard_delete_file):
    mock_db = mock.AsyncMock()
    mock_soft_delete_file.return_value = DeleteFileEnum.DELETED

    result = await delete_file(name="test.txt", destination="folder", delete_permanently=False, db=mock_db)

    assert result == {"message": "File test.txt deleted."}
    mock_soft_delete_file.assert_awaited_once_with(mock_db, file_name="test.txt", destination="folder")
    mock_logger.info.assert_called_with("File test.txt deleted.")


@pytest.mark.asyncio
@mock.patch("app.api.routes.delete.hard_delete_file")
@mock.patch("app.api.routes.delete.soft_delete_file")
@mock.patch("app.api.routes.delete.logger")
async def test_delete_file_soft_not_found(mock_logger, mock_soft_delete_file, mock_hard_delete_file):
    mock_db = mock.AsyncMock()
    mock_soft_delete_file.return_value = DeleteFileEnum.FILE_NOT_FOUND

    with pytest.raises(HTTPException) as exc_info:
        await delete_file(name="missing.txt", destination="", delete_permanently=False, db=mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "File missing.txt not found."


@pytest.mark.asyncio
@mock.patch("app.api.routes.delete.hard_delete_file")
@mock.patch("app.api.routes.delete.soft_delete_file")
@mock.patch("app.api.routes.delete.logger")
async def test_delete_file_soft_error(mock_logger, mock_soft_delete_file, mock_hard_delete_file):
    mock_db = mock.AsyncMock()
    mock_soft_delete_file.return_value = DeleteFileEnum.ERROR

    with pytest.raises(HTTPException) as exc_info:
        await delete_file(name="error.txt", destination="", delete_permanently=False, db=mock_db)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Error deleting file error.txt."


@pytest.mark.asyncio
@mock.patch("app.api.routes.delete.hard_delete_file")
@mock.patch("app.api.routes.delete.soft_delete_file")
@mock.patch("app.api.routes.delete.logger")
async def test_delete_file_hard_success(mock_logger, mock_soft_delete_file, mock_hard_delete_file):
    mock_db = mock.AsyncMock()
    mock_hard_delete_file.return_value = DeleteFileEnum.DELETED

    result = await delete_file(name="hard.txt", destination="dir", delete_permanently=True, db=mock_db)

    assert result == {"message": "File hard.txt deleted permanently."}
    mock_hard_delete_file.assert_awaited_once_with(mock_db, file_name="hard.txt", destination="dir")
    mock_logger.info.assert_called_with("File hard.txt deleted permanently.")


@pytest.mark.asyncio
@mock.patch("app.api.routes.delete.hard_delete_file")
@mock.patch("app.api.routes.delete.soft_delete_file")
@mock.patch("app.api.routes.delete.logger")
async def test_delete_file_hard_not_found(mock_logger, mock_soft_delete_file, mock_hard_delete_file):
    mock_db = mock.AsyncMock()
    mock_hard_delete_file.return_value = DeleteFileEnum.FILE_NOT_FOUND

    with pytest.raises(HTTPException) as exc_info:
        await delete_file(name="nofile.txt", destination="", delete_permanently=True, db=mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "File nofile.txt not found."


@pytest.mark.asyncio
@mock.patch("app.api.routes.delete.hard_delete_file")
@mock.patch("app.api.routes.delete.soft_delete_file")
@mock.patch("app.api.routes.delete.logger")
async def test_delete_file_hard_error(mock_logger, mock_soft_delete_file, mock_hard_delete_file):
    mock_db = mock.AsyncMock()
    mock_hard_delete_file.return_value = DeleteFileEnum.ERROR

    with pytest.raises(HTTPException) as exc_info:
        await delete_file(name="fail.txt", destination="", delete_permanently=True, db=mock_db)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Error deleting file fail.txt permanently."
