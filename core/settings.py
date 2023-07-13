"""Settings for the project."""

from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Base Settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PROJECT_NAME: str = "Serverless"

    PROJECT_DESCRIPTION: str = (
        "A serverless server, that help you add serverless functions to your project."
    )

    PROJECT_VERSION: str = "0.1.0"

    PORT: int = 8000

    DOCS_URL: str = "/docs"

    REDOC_URL: str = "/redoc"

    OPENAPI_URL: str = "/openapi.json"

    ALLOWED_HOSTS: ClassVar[list[str]] = ["*"]

    CORS_ORIGINS: ClassVar[list[str]] = ["*"]

    CORS_ALLOW_METHODS: ClassVar[list[str]] = ["*"]

    CORS_ALLOW_HEADERS: ClassVar[list[str]] = ["*"]

    CORS_ALLOW_CREDENTIALS: bool = True

    SECRET_KEY: str = "secret"


settings = Settings()
