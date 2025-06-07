import pytest
from unittest import mock
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import db_config


@pytest.fixture
def mock_settings():
    with mock.patch("app.core.database.db_config.settings") as mock_settings:
        mock_settings.DB_URL = "postgresql+asyncpg:///:memory:"
        mock_settings.DB_POOL_SIZE = 5
        mock_settings.DB_MAX_OVERFLOW = 10
        yield mock_settings


@pytest.fixture
def mock_logger():
    with mock.patch("app.core.database.db_config.get_logger") as mock_logger:
        yield mock_logger


@pytest.mark.asyncio
async def test_database_initialization(mock_settings, mock_logger):
    db = db_config.Database()
    assert db.engine is not None
    assert db.session_local is not None


@pytest.mark.asyncio
async def test_get_session_yields_asyncsession(mock_settings, mock_logger):
    db = db_config.Database()
    async with db.session_local() as session:
        assert isinstance(session, AsyncSession)

    # Test the async generator
    gen = db.get_session()
    session = await gen.__anext__()
    assert isinstance(session, AsyncSession)
    with pytest.raises(StopAsyncIteration):
        await gen.__anext__()


@pytest.mark.asyncio
async def test_get_db_yields_asyncsession(mock_settings, mock_logger):
    # Patch db to use a new Database instance with in-memory DB
    with mock.patch.object(db_config, "db", db_config.Database()):
        gen = db_config.get_db()
        session = await gen.__anext__()
        assert isinstance(session, AsyncSession)
        with pytest.raises(StopAsyncIteration):
            await gen.__anext__()
