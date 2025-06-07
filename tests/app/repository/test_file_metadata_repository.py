import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.entity.file_metadata import FileMetadata
from sqlalchemy.exc import SQLAlchemyError

import app.repository.file_metadata_repository as repo


@pytest.fixture
def file_metadata():
    return FileMetadata(
        file_name="test.txt",
        file_size=123,
        destination="folder",
        is_deleted=False,
        tags="tag1,tag2",
        description="Test file",
        user_id="user123",
        version=1,
        file_type="text/plain",
        file_path="/path/to/test.txt",
        created_at="2023-10-01 00:00:00",
        updated_at="2023-10-01 00:00:00",
    )


@pytest.fixture
def db_session():
    return AsyncMock()


@pytest.mark.asyncio
async def test_insert_success(db_session, file_metadata):
    db_session.add = MagicMock()
    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock()
    with patch.object(repo.logger, "debug") as mock_log:
        result = await repo.insert(db_session, file_metadata)
        db_session.add.assert_called_once_with(file_metadata)
        db_session.commit.assert_awaited_once()
        db_session.refresh.assert_awaited_once_with(file_metadata)
        mock_log.assert_called()
        assert result == file_metadata


@pytest.mark.asyncio
async def test_insert_sqlalchemy_error(db_session, file_metadata):
    db_session.add = MagicMock()
    db_session.commit = AsyncMock(side_effect=SQLAlchemyError("fail"))
    db_session.rollback = AsyncMock()
    with patch.object(repo.logger, "error") as mock_log:
        with pytest.raises(SQLAlchemyError):
            await repo.insert(db_session, file_metadata)
        db_session.rollback.assert_awaited_once()
        mock_log.assert_called()


@pytest.mark.asyncio
async def test_delete_found(db_session, file_metadata):
    db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=file_metadata))
    )
    db_session.delete = AsyncMock()
    db_session.commit = AsyncMock()
    with patch.object(repo.logger, "debug") as mock_log:
        await repo.delete(db_session, "test.txt")
        db_session.delete.assert_awaited_once_with(file_metadata)
        db_session.commit.assert_awaited_once()
        mock_log.assert_called()


@pytest.mark.asyncio
async def test_delete_not_found(db_session):
    db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )
    with patch.object(repo.logger, "warning") as mock_log:
        await repo.delete(db_session, "notfound.txt")
        mock_log.assert_called()


@pytest.mark.asyncio
async def test_delete_sqlalchemy_error(db_session):
    db_session.execute = AsyncMock(side_effect=SQLAlchemyError("fail"))
    db_session.rollback = AsyncMock()
    with patch.object(repo.logger, "error") as mock_log:
        with pytest.raises(SQLAlchemyError):
            await repo.delete(db_session, "test.txt")
        db_session.rollback.assert_awaited_once()
        mock_log.assert_called()


@pytest.mark.asyncio
async def test_get_file_by_name_found(db_session, file_metadata):
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [file_metadata]
    db_session.execute = AsyncMock(
        return_value=MagicMock(scalars=MagicMock(return_value=mock_scalars))
    )
    with patch.object(repo.logger, "debug") as mock_log:
        result = await repo.get_file_by_name(db_session, "test.txt")
        assert result == [file_metadata]
        mock_log.assert_called()


@pytest.mark.asyncio
async def test_get_file_by_name_not_found(db_session):
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    db_session.execute = AsyncMock(
        return_value=MagicMock(scalars=MagicMock(return_value=mock_scalars))
    )
    with patch.object(repo.logger, "warning") as mock_log:
        result = await repo.get_file_by_name(db_session, "notfound.txt")
        assert result == []
        mock_log.assert_called()


@pytest.mark.asyncio
async def test_get_file_by_name_sqlalchemy_error(db_session):
    db_session.execute = AsyncMock(side_effect=SQLAlchemyError("fail"))
    with patch.object(repo.logger, "error") as mock_log:
        with pytest.raises(SQLAlchemyError):
            await repo.get_file_by_name(db_session, "test.txt")
        mock_log.assert_called()


@pytest.mark.asyncio
async def test_get_file_by_name_and_destination_found(db_session, file_metadata):
    db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=file_metadata))
    )
    with patch.object(repo.logger, "debug") as mock_log:
        result = await repo.get_file_by_name_and_destination(
            db_session, "test.txt", "folder"
        )
        assert result == file_metadata
        mock_log.assert_called()


@pytest.mark.asyncio
async def test_get_file_by_name_and_destination_not_found(db_session):
    db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )
    with patch.object(repo.logger, "warning") as mock_log:
        result = await repo.get_file_by_name_and_destination(
            db_session, "notfound.txt", "folder"
        )
        assert result is None
        mock_log.assert_called()


@pytest.mark.asyncio
async def test_get_file_by_name_and_destination_sqlalchemy_error(db_session):
    db_session.execute = AsyncMock(side_effect=SQLAlchemyError("fail"))
    with patch.object(repo.logger, "error") as mock_log:
        with pytest.raises(SQLAlchemyError):
            await repo.get_file_by_name_and_destination(
                db_session, "test.txt", "folder"
            )
        mock_log.assert_called()


@pytest.mark.asyncio
async def test_get_file_by_name_and_destination_for_hard_delete_found(
    db_session, file_metadata
):
    db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=file_metadata))
    )
    with patch.object(repo.logger, "debug") as mock_log:
        result = await repo.get_file_by_name_and_destination_for_hard_delete(
            db_session, "test.txt", "folder"
        )
        assert result == file_metadata
        mock_log.assert_called()


@pytest.mark.asyncio
async def test_get_file_by_name_and_destination_for_hard_delete_not_found(db_session):
    db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )
    with patch.object(repo.logger, "warning") as mock_log:
        result = await repo.get_file_by_name_and_destination_for_hard_delete(
            db_session, "notfound.txt", "folder"
        )
        assert result is None
        mock_log.assert_called()


@pytest.mark.asyncio
async def test_get_file_by_name_and_destination_for_hard_delete_sqlalchemy_error(
    db_session,
):
    db_session.execute = AsyncMock(side_effect=SQLAlchemyError("fail"))
    with patch.object(repo.logger, "error") as mock_log:
        with pytest.raises(SQLAlchemyError):
            await repo.get_file_by_name_and_destination_for_hard_delete(
                db_session, "test.txt", "folder"
            )
        mock_log.assert_called()


@pytest.mark.asyncio
async def test_update_success(db_session, file_metadata):
    db_session.merge = AsyncMock()
    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock()
    with patch.object(repo.logger, "debug") as mock_log:
        result = await repo.update(db_session, file_metadata)
        db_session.merge.assert_awaited_once_with(file_metadata)
        db_session.commit.assert_awaited_once()
        db_session.refresh.assert_awaited_once_with(file_metadata)
        assert result == file_metadata
        mock_log.assert_called()


@pytest.mark.asyncio
async def test_update_sqlalchemy_error(db_session, file_metadata):
    db_session.merge = AsyncMock(side_effect=SQLAlchemyError("fail"))
    db_session.rollback = AsyncMock()
    with patch.object(repo.logger, "error") as mock_log:
        with pytest.raises(SQLAlchemyError):
            await repo.update(db_session, file_metadata)
        db_session.rollback.assert_awaited_once()
        mock_log.assert_called()


@pytest.mark.asyncio
async def test_get_list_basic(db_session, file_metadata):
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [file_metadata]
    db_session.execute = AsyncMock(
        return_value=MagicMock(scalars=MagicMock(return_value=mock_scalars))
    )
    with patch.object(repo.logger, "debug") as mock_log:
        result = await repo.get_list(db_session)
        assert result == [file_metadata]
        mock_log.assert_called()


@pytest.mark.asyncio
async def test_get_list_sqlalchemy_error(db_session):
    db_session.execute = AsyncMock(side_effect=SQLAlchemyError("fail"))
    with patch.object(repo.logger, "error") as mock_log:
        with pytest.raises(SQLAlchemyError):
            await repo.get_list(db_session)
        mock_log.assert_called()


@pytest.mark.asyncio
async def test_get_list_order_by_name(db_session):
    # Create some test data
    file1 = FileMetadata(file_name="b.txt", file_size=100)
    file2 = FileMetadata(file_name="a.txt", file_size=200)

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [file2, file1]  # Sorted by name
    db_session.execute = AsyncMock(
        return_value=MagicMock(scalars=MagicMock(return_value=mock_scalars))
    )

    result = await repo.get_list(db_session, order_by_name=True)
    assert result == [file2, file1]  # Assert ordered by name


@pytest.mark.asyncio
async def test_get_list_order_by_size(db_session):
    # Create some test data
    file1 = FileMetadata(file_name="test1.txt", file_size=200)
    file2 = FileMetadata(file_name="test2.txt", file_size=100)

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [file2, file1]  # Sorted by size
    db_session.execute = AsyncMock(
        return_value=MagicMock(scalars=MagicMock(return_value=mock_scalars))
    )

    result = await repo.get_list(db_session, order_by_size=True)
    assert result == [file2, file1]  # Assert ordered by size


@pytest.mark.asyncio
async def test_get_list_order_by_updated_at(db_session):
    # Create some test data
    file1 = FileMetadata(file_name="old.txt", updated_at="2024-01-01")
    file2 = FileMetadata(file_name="new.txt", updated_at="2024-01-02")

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [file2, file1]  # Sorted by updated_at desc
    db_session.execute = AsyncMock(
        return_value=MagicMock(scalars=MagicMock(return_value=mock_scalars))
    )

    result = await repo.get_list(db_session, order_by_updated_at=True)
    assert result == [file2, file1]  # Assert ordered by updated_at desc


@pytest.mark.asyncio
async def test_get_list_filter_by_tag(db_session):
    # Create some test data
    file1 = FileMetadata(file_name="test1.txt", tags="tag1,tag2")

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [file1]
    db_session.execute = AsyncMock(
        return_value=MagicMock(scalars=MagicMock(return_value=mock_scalars))
    )

    result = await repo.get_list(db_session, tag="tag1")
    assert result == [file1]


@pytest.mark.asyncio
async def test_get_list_filter_by_destination(db_session):
    # Create some test data
    file1 = FileMetadata(file_name="test1.txt", destination="folder1")
    file2 = FileMetadata(file_name="test2.txt", destination="folder1/subfolder")

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [file1, file2]
    db_session.execute = AsyncMock(
        return_value=MagicMock(scalars=MagicMock(return_value=mock_scalars))
    )

    result = await repo.get_list(db_session, destination="folder1")
    assert result == [file1, file2]  # Should include both main folder and subfolder
