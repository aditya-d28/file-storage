from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Integer,
    String,
    Text,
    func,
)

from .base import Base


class FileMetadata(Base):
    __tablename__ = "file_metadata"

    file_id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(1024), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50))
    destination = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(), server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP(),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    tags = Column(String, nullable=True)
    version = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<FileMetadata(file_name={self.file_name}, file_size={self.file_size})>"
