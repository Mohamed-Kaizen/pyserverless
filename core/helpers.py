"""Helper functions for the project."""
import json
from datetime import datetime, timezone
from pathlib import Path

import tomlkit
from fastapi import Request
from pydantic import BaseModel


def get_deps(root_path: Path) -> dict:
    """Get all packages."""
    with Path.open(root_path.joinpath("pyproject.toml")) as file:
        pyproject = tomlkit.parse(file.read())

        main_deps = pyproject["tool"]["poetry"]["dependencies"]

        return {
            key: value
            for key, value in main_deps.items()
            if key not in ["python", "fastapi", "uvicorn", "watchfiles"]
        }


async def fn_log(request: Request, response: dict) -> None:
    """Log the request and response of function."""
    fn_name = request.url.path.split("/fn/")[1]
    if not Path(f"logs/{fn_name}.json").exists():
        return

    req_data = {}

    req_headers = request.headers

    if req_headers.get("content-type") == "application/x-www-form-urlencoded":
        req_data = await request.form()

    if req_headers.get("content-type") == "application/json":
        req_data = await request.json()

    req = {
        "headers": req_headers,
        "cookies": request.cookies,
        "data": req_data,
    }

    log_data = {
        "date": datetime.now(timezone.utc),
        "method": request.method,
        "request": req,
        "response": response,
    }

    with Path.open(f"logs/{fn_name}.json", "r") as fr:
        data = json.load(fr)

        data.get("logs").append(log_data)

        logs = Logs(**data)

        with Path.open(f"logs/{fn_name}.json", "w") as fw:
            fw.write(logs.json())


async def set_body(request: Request, body: bytes) -> None:
    """Helper function to set _receive in the request."""

    async def receive() -> dict:
        return {"type": "http.request", "body": body}

    request._receive = receive


class RequestLogData(BaseModel):
    """Request log data."""

    headers: dict

    cookies: dict

    data: dict


class ResponseLogData(BaseModel):
    """Response log data."""

    headers: dict

    status_code: int

    data: str


class LogData(BaseModel):
    """Log data."""

    date: datetime

    method: str

    request: RequestLogData

    response: ResponseLogData


class Logs(BaseModel):
    """Logs model."""

    logs: list[LogData]
