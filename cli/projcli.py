"""
# Project Management CLI
This CLI subcommand deals with managing the BookString project itself. For now it's entirely
informational but as the project develops we can add common development patterns here to enforce
standardization.
"""

from pathlib import Path
from pydantic import BaseModel, Field

import typer

from config import Config
from appcli import manager as app_manager
from servercli import manager as server_manager

from typing import Dict


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