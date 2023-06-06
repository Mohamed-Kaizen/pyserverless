"""The main file for the project."""
import importlib
import json
import logging
import os
from collections.abc import Callable
from pathlib import Path

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.background import BackgroundTask
from starlette.middleware.cors import CORSMiddleware

from core.functions import router as functions_router
from core.helpers import fn_log, set_body
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


@app.middleware("http")
async def logs_middleware(request: Request, call_next: Callable) -> Response:
    """A log middleware."""
    fn_path = "/fn/" in request.url.path

    if fn_path:
        req_body = await request.body()
        await set_body(request, req_body)

    response = await call_next(request)

    res_body = b""
    async for chunk in response.body_iterator:
        res_body += chunk

    if fn_path:
        rep = {
            "headers": response.headers,
            "status_code": response.status_code,
            "data": res_body,
        }

        task = BackgroundTask(fn_log, request, rep)

        return Response(
            content=res_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
            background=task,
        )

    return Response(
        content=res_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
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

                if not Path(f"logs/{module}.json").exists():
                    with Path.open(f"logs/{module}.json", "w") as f:
                        json.dump({"logs": []}, f)

                for method in ["get", "post", "patch", "put", "delete"]:
                    if hasattr(fn, method):
                        app.add_api_route(
                            f"/fn/{module}",
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
