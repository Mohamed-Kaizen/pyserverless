"""The main file for the project."""
import os

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from core.functions import router as functions_router  # noqa: I202
from core.packages import router as packages_router  # noqa: I202
from core.settings import settings  # noqa: I202

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

app.include_router(packages_router, prefix="/packages", tags=["packages"])
app.include_router(
    functions_router, prefix="/functions-management", tags=["functions management"]
)


@app.on_event("startup")
async def get_functions() -> None:
    """Get all the functions."""
    for file in os.listdir("functions"):

        if file.endswith(".py") and file != "__init__.py":

            module = file.split(".")[0]

            try:
                router = __import__(f"functions.{module}", fromlist=["router"]).router

                app.include_router(router, prefix=f"/{module}", tags=["functions"])

            except ImportError:
                print(f"Failed to import {module}")

            except AttributeError:
                print("Router should be a APIRouter instance")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        log_level="info",
        reload=True,
        reload_includes=["*.py", "pyproject.toml", "functions/*"],
    )
