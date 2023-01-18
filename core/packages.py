"""A module to handle the packages."""
import subprocess  # noqa: S404

import tomlkit
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class InstallPackage(BaseModel):
    """Install package model."""

    name: str

    version: str = "latest"

    scope: str = "global"


class UninstallPackage(BaseModel):
    """Uninstall package model."""

    name: str

    scope: str = "global"


@router.post("/install")
def install(package: InstallPackage) -> str:
    """Install packages."""
    scope = package.scope.lower()

    return (
        subprocess.run(  # noqa: S603,S607
            ["poetry", "add", f"{package.name}@{package.version}"],
            capture_output=True,
        ).stdout.decode("utf-8")
        if scope == "global"
        else subprocess.run(  # noqa: S603,S607
            [
                "poetry",
                "add",
                f"{package.name}@{package.version}",
                "--group",
                f"{scope}",
            ],
            capture_output=True,
        ).stdout.decode("utf-8")
    )


@router.post("/remove")
def remove(package: UninstallPackage) -> str:
    """Remove packages."""
    scope = package.scope.lower()
    return (
        subprocess.run(  # noqa: S603,S607
            ["poetry", "remove", f"{package.name}"], capture_output=True
        ).stdout.decode("utf-8")
        if scope == "global"
        else subprocess.run(  # noqa: S603,S607
            ["poetry", "remove", f"{package.name}", "--group", f"{scope}"],
            capture_output=True,
        ).stdout.decode("utf-8")
    )


@router.post("/update")
def update(package: InstallPackage) -> str:
    """Update packages."""
    scope = package.scope.lower()

    return (
        subprocess.run(  # noqa: S603,S607
            ["poetry", "update", f"{package.name}"], capture_output=True
        ).stdout.decode("utf-8")
        if scope == "global"
        else subprocess.run(  # noqa: S603,S607
            ["poetry", "update", f"{package.name}", "--with", f"{scope}"],
            capture_output=True,
        ).stdout.decode("utf-8")
    )


@router.get("/list")
def list_packages() -> dict:
    """Get all packages."""
    deps = {}

    with open("pyproject.toml") as file:
        pyproject = tomlkit.parse(file.read())

        main_deps = pyproject["tool"]["poetry"]["dependencies"]

        global_deps = {
            key: value
            for key, value in main_deps.items()
            if key not in ["python", "fastapi", "uvicorn", "watchfiles"]
        }

        group_deps = {
            key: value
            for key, value in pyproject["tool"]["poetry"]["group"].items()
            if key != "dev"
        }

        for dep in group_deps:
            deps[dep] = group_deps[dep]["dependencies"]

        deps["global"] = global_deps

    return deps


@router.get("/list/{scope}")
def list_packages_by_scope(scope: str) -> dict:
    """List packages by scope."""
    deps = {}

    scope = scope.lower()

    with open("pyproject.toml") as file:
        pyproject = tomlkit.parse(file.read())

        main_deps = pyproject["tool"]["poetry"]["dependencies"]

        global_deps = {
            key: value
            for key, value in main_deps.items()
            if key not in ["python", "fastapi", "uvicorn", "watchfiles"]
        }

        group_deps = {
            key: value
            for key, value in pyproject["tool"]["poetry"]["group"].items()
            if key != "dev"
        }

        for dep in group_deps:
            deps[dep] = group_deps[dep]["dependencies"]

        deps["global"] = global_deps

    return deps.get(scope, {})
