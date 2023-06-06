"""A module for functions management."""
import json
from pathlib import Path
from typing import TypedDict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.helpers import LogData, Logs

router = APIRouter()

root_path = Path(__file__).parent.parent

functions_path = root_path.joinpath("functions")

logs_path = root_path.joinpath("logs")

logs_path.mkdir(exist_ok=True)


class Response(TypedDict):
    """Response type for dict."""

    detail: str


class FunctionCreation(BaseModel):
    """Function creation model."""

    name: str

    code: str

    class Config:
        """Config."""

        schema_extra = {
            "example": {
                "name": "hello",
                "code": "def get() -> str:\n\n\treturn 'hello'\n\n",
            },
        }


class FunctionDeletion(BaseModel):
    """Function deletion model."""

    name: str

    class Config:
        """Config."""

        schema_extra = {"example": {"name": "hello"}}


class FunctionUpdate(FunctionCreation):
    """Function update model."""

    class Config:
        """Config."""

        schema_extra = {
            "example": {
                "name": "hello",
                "code": "def get() -> str:\n\n\treturn 'hello world'\n\n",
            },
        }


@router.post("/create")
def create(function: FunctionCreation) -> Response:
    """Create new function."""
    fn = functions_path.joinpath(f"{function.name}.py")

    if fn.exists():
        raise HTTPException(status_code=400, detail="Function already exists")

    with Path.open(fn, "w") as f:
        f.write(function.code)

    with Path.open(logs_path.joinpath(f"{function.name}.json"), "w") as f:
        json.dump({"logs": []}, f)

    return {"detail": "Function has been created"}


@router.post("/update")
def update_function(function: FunctionUpdate) -> Response:
    """Update a function."""
    fn = functions_path.joinpath(f"{function.name}.py")

    if not fn.exists():
        raise HTTPException(status_code=400, detail="Function does not exist")

    with Path.open(fn, "w") as f:
        f.write(function.code)

    return {"detail": "Function has been updated"}


@router.post("/delete")
def delete(function: FunctionDeletion) -> Response:
    """Delete a function."""
    fn = functions_path.joinpath(f"{function.name}.py")

    Path.unlink(fn, missing_ok=True)

    logs_path.joinpath(f"{function.name}.json").unlink(missing_ok=True)

    return {"detail": "Function has been deleted"}


@router.get("/list")
def get_functions() -> list[str]:
    """Get functions."""
    return [
        fn.name.replace(".py", "")
        for fn in functions_path.glob("*.py")
        if fn.is_file() and fn.name != "__init__.py"
    ]


@router.get("/get")
def get_function(name: str) -> Response:
    """Get a function."""
    try:
        with Path.open(functions_path.joinpath(f"{name}.py")) as f:
            return {"detail": f.read()}
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail="Function does not exist") from e


@router.get("/logs")
def get_logs(fn_name: str) -> list[LogData]:
    """Get all logs of function."""
    fn_log_path = Path(f"logs/{fn_name}.json")

    if not fn_log_path.exists():
        raise HTTPException(status_code=400, detail="Log does not exist")

    with Path.open(f"logs/{fn_name}.json", "r") as fr:
        data = json.load(fr)

        return Logs(**data).logs
