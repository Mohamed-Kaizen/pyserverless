"""A module to handle the packages."""
import subprocess
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from core.helpers import get_deps

router = APIRouter()


root_path = Path(__file__).parent.parent


class InstallPackage(BaseModel):
    """Install package model."""

    name: str

    version: str = "latest"


@router.post("/install")
def install(package: InstallPackage) -> str:
    """Install packages."""
    return subprocess.run(
        ["poetry", "add", f"{package.name}@{package.version}"],  # noqa
        capture_output=True,
    ).stdout.decode("utf-8")


@router.post("/remove")
def remove(name: str) -> str:
    """Remove packages."""
    return subprocess.run(
        ["poetry", "remove", f"{name}"],  # noqa
        capture_output=True,
    ).stdout.decode("utf-8")


@router.get("/list")
def list_packages() -> dict:
    """Get all packages."""
    return get_deps(root_path)
