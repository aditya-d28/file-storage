from abc import ABC, abstractmethod

from fastapi import UploadFile

from app.model.upload_model import StorageUploadResponseModel


class StorageBase(ABC):
    @abstractmethod
    def upload(self, name: str, file: UploadFile, destination: str) -> StorageUploadResponseModel:
        pass

    @abstractmethod
    def delete(self, name: str, destination: str) -> None:
        pass
