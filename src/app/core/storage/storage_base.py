from abc import ABC, abstractmethod

from app.model.upload_model import StorageUploadResponseModel
from fastapi import UploadFile


class StorageBase(ABC):
    @abstractmethod
    def upload(self, name: str, file: UploadFile, destination: str) -> StorageUploadResponseModel:
        pass

    @abstractmethod
    def delete(self, name: str, destination: str) -> None:
        pass
