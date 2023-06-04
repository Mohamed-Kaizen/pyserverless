"""Settings for the project."""
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Base Settings."""

    PROJECT_NAME: str = "Serverless"

    PROJECT_DESCRIPTION: str = (
        "A serverless server, that help you add serverless functions to your project."
    )

    PROJECT_VERSION: str = "0.1.0"

    PORT: int = 8000

    DOCS_URL: str = "/docs"

    REDOC_URL: str = "/redoc"

    OPENAPI_URL: str = "/openapi.json"

    ALLOWED_HOSTS: list[str] = ["*"]

    CORS_ORIGINS: list[str] = ["*"]

    CORS_ALLOW_METHODS: list[str] = ["*"]

    CORS_ALLOW_HEADERS: list[str] = ["*"]

    CORS_ALLOW_CREDENTIALS: bool = True

    SECRET_KEY: str = "secret"

    class Config:
        """Override the default config."""

        env_file = ".env"


settings = Settings()
