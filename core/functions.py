"""A module for functions management."""
import os

import tomlkit
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class FunctionCreation(BaseModel):
    """Function creation model."""

    name: str

    code: str

    class Config:
        """Config."""

        schema_extra = {
            "example": {
                "name": "hello",
                "code": "from fastapi import APIRouter\n\nrouter = APIRouter()"
                "\n\n\n@router.post('/')\ndef hello() -> str:\n\n\treturn 'hello'\n\n",
            }
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
                "code": "from fastapi import APIRouter\n\nrouter = APIRouter()"
                "\n\n\n"
                "@router.post('/')\ndef hello() -> str:\n\n\treturn 'hello world'\n\n",
            }
        }


@router.post("/create")
def create(function: FunctionCreation) -> str:
    """Create a function."""
    with open("functions.toml", "r+") as f:
        functions = tomlkit.parse(f.read()).get("functions", [])

        if function.name in [f["name"] for f in functions]:
            raise HTTPException(status_code=400, detail="Function already exists")

        functions.append({"name": function.name, "code": function.code})

        f.write(tomlkit.dumps({"functions": functions}))

    with open(f"functions/{function.name}.py", "w") as f:
        f.write(function.code)

    return "Function has been created"


@router.post("/delete")
def delete(function: FunctionDeletion) -> str:
    """Delete a function."""
    with open("functions.toml", "r") as f:
        functions = tomlkit.parse(f.read()).get("functions", [])

        if function.name not in [f["name"] for f in functions]:
            raise HTTPException(status_code=400, detail="Function does not exist")

        functions = [f for f in functions if f["name"] != function.name]

        with open("functions.toml", "w") as _f:
            data = {"functions": functions} if functions else {}
            _f.write(tomlkit.dumps(data))

    os.remove(f"functions/{function.name}.py")

    return "Function has been deleted"


@router.get("/list")
def get_functions() -> list:
    """Get functions."""
    with open("functions.toml", "r") as f:
        functions = tomlkit.parse(f.read()).get("functions", [])

        return [{"name": f["name"], "lang": "python"} for f in functions]


@router.get("/get")
def get_function(name: str) -> dict:
    """Get a function."""
    try:
        with open(f"functions/{name}.py") as f:
            return {"code": f.read()}
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail="Function does not exist") from e


@router.post("/update")
def update_function(function: FunctionUpdate) -> str:
    """Update a function."""
    try:
        with open(f"functions/{function.name}.py", "w") as f:
            f.write(function.code)

        with open("functions.toml", "r") as f:

            functions = tomlkit.parse(f.read()).get("functions", [])

            for fn in functions:
                if fn["name"] == function.name:
                    fn["code"] = function.code

            with open("functions.toml", "w") as _f:
                _f.write(tomlkit.dumps({"functions": functions}))

        return "Function has been updated"
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail="Function does not exist") from e
