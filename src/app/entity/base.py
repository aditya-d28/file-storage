from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all SQLAlchemy models.

    This class serves as the base for all SQLAlchemy models in the application.
    It inherits from `AsyncAttrs` and `DeclarativeBase` to support asynchronous operations.
    """

    pass
