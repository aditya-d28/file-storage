import os
from typing import Annotated, Any

from pydantic import AnyUrl, BeforeValidator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = os.path.join(os.path.dirname(__file__), "../../../.env")


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_path, env_ignore_empty=True, extra="ignore")
    API_VER_STR: str = "/v1"
    PROJECT_NAME: str
    CONSOLE_LOG_LEVEL: str
    FILE_LOG_LEVEL: str
    DEV_MODE: str
    DB_TYPE: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_POOL_SIZE: int
    DB_MAX_OVERFLOW: int
    STORAGE_TYPE: str
    STORAGE_BUCKET_NAME: str
    S3_ENDPOINT_URL: str | None = None
    STORAGE_AWS_ACCESS_KEY_ID: str | None = None
    STORAGE_AWS_SECRET_ACCESS_KEY: str | None = None
    STORAGE_REGION_NAME: str | None = None
    STORAGE_GCS_LOCATION: str | None = None

    ALLOWED_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    @computed_field
    @property
    def DB_URL(self) -> str:
        if self.DB_TYPE == "sqlite":
            return f"sqlite+aiosqlite:///{self.DB_NAME}"

        if self.DB_TYPE == "postgresql":
            return (
                f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )

        if self.DB_TYPE == "mysql":
            return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def ALLOWED_ORIGINS_LIST(self) -> list[str]:
        if self.DEV_MODE == "Y":
            return ["*"]
        return self.ALLOWED_ORIGINS


settings = Settings()  # type: ignore
