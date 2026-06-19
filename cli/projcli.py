"""
# Project Management CLI
This CLI subcommand deals with managing the BookString project itself. For now it's entirely
informational but as the project develops we can add common development patterns here to enforce
standardization.
"""

from tomllib import load
import subprocess
from pathlib import Path
from pydantic import BaseModel, Field

import typer

from config import Config #type: ignore
from appcli import manager as app_manager #type: ignore
from servercli import manager as server_manager #type: ignore
from docgen import PythonDirectory #type: ignore

from typing import Dict, List, Tuple


class ProjectStatus(BaseModel):
    version: str
    branch: str
    commit_hash: str
    changes: List[Tuple[str, ...]]


class ProjectManager(BaseModel):
    config: Config = Field(default_factory=Config.load)
    root: Path = Path(".")

    @property
    def paths(self) -> Dict[str, Path]:
        """
        All the important directory paths in the project.
        """
        return {
            "root": self.root,
            "cli": self.root / "cli",
            "app": self.root / app_manager.root,
            "server": self.root / server_manager.root,
        }

    @property
    def models_schema_path(self) -> Path:
        return self.paths["app"] / self.config.models["schema_file"]

    @property
    def typedefs_path(self) -> Path:
        return self.paths["app"] / "src" / "models.d.ts"

    @property
    def pyproject(self) -> Dict:
        with Path("pyproject.toml").open("rb") as f:
            return load(f)

    @property
    def status(self) -> ProjectStatus:
        return ProjectStatus(
            version=self.pyproject["project"]["version"],
            branch=subprocess.run([
                "git", "branch", "--show-current"
            ], capture_output=True).stdout.decode().strip(),
            commit_hash=subprocess.run([
                "git", "rev-parse", "--short", "HEAD"
            ], capture_output=True).stdout.decode().strip(),
            changes=[
                tuple(line.strip().split(" "))
                for line in subprocess.run([
                "git", "status", "--porcelain"
            ], capture_output=True).stdout.decode().strip().split("\n")
            ]
        )


manager = ProjectManager()
project_app = typer.Typer()

@project_app.command("sync")
def project_sync_models():
    """
    Synchronize models from server to app
    """
    server_manager.write_model_schemas_to(manager.models_schema_path)
    app_manager.build_types(
        manager.models_schema_path.relative_to(manager.paths["app"]),
        manager.typedefs_path.relative_to(manager.paths["app"]),
    )


@project_app.command("dump-config")
def project_dump_config():
    """
    Dumps the current project config to console as JSON
    """
    print(manager.config.model_dump_json())


@project_app.command("status")
def project_status():
    """
    Dumps the current project status to console as JSON
    """
    print(manager.status.model_dump_json())


@project_app.command("pydocs")
def project_docs(target: Path, output: Path):
    """
    Generate XML docs for the target python project to the output path
    """
    if not target.is_dir():
        raise FileNotFoundError(f"Cannot find target directory '{target}'")

    pyproj = PythonDirectory.parse_directory(target)
    with output.open("w") as f:
        f.write(pyproj.xml)