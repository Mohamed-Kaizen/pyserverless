"""The main file for the project."""
import importlib
import logging
import os

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.middleware.cors import CORSMiddleware

from core.functions import router as functions_router
from core.packages import router as packages_router
from core.settings import settings

logger = logging.getLogger()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    openapi_url=settings.OPENAPI_URL,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

api_key_header = APIKeyHeader(name="x-api-key")


def admin(api_key: str = Security(api_key_header)) -> None:  # noqa
    """Allow routes only to be accessed by admin."""
    if api_key != settings.SECRET_KEY:
        raise HTTPException(status_code=401, detail="invalid api key")


app.include_router(
    packages_router,
    prefix="/packages",
    tags=["packages"],
    dependencies=[Depends(admin)],
)

app.include_router(
    functions_router,
    prefix="/functions-management",
    tags=["functions management"],
    dependencies=[Depends(admin)],
)


@app.on_event("startup")
async def get_functions() -> None:
    """Get all the functions."""
    for file in os.listdir("functions"):
        if file.endswith(".py") and file != "__init__.py":
            module = file.split(".")[0]

            try:
                fn = importlib.import_module(f"functions.{module}")

                for method in ["get", "post", "patch", "put", "delete"]:
                    if hasattr(fn, method):
                        app.add_api_route(
                            f"/{module}",
                            getattr(fn, method),
                            methods=[method.upper()],
                            tags=[f"{module}"],
                        )

            except ImportError:
                logger.exception("Import error")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # noqa
        port=settings.PORT,
        log_level="info",
        reload=True,
        reload_includes=["*.py", "pyproject.toml", "functions/*"],
    )
