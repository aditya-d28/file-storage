from enum import Enum


class DeleteFileEnum(str, Enum):
    DELETED = "deleted"
    FILE_NOT_FOUND = "file_not_found"
    ERROR = "error"
