"""A module for functions management."""
from pathlib import Path
from typing import TypedDict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

root_path = Path(__file__).parent.parent

functions_path = root_path.joinpath("functions")


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

    if not fn.exists():
        raise HTTPException(status_code=400, detail="Function does not exist")

    Path.unlink(root_path.joinpath(f"functions/{function.name}.py"))

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
