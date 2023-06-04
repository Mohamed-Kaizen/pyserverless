"""Helper functions for the project."""
from pathlib import Path

import tomlkit


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
