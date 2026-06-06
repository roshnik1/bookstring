"""
# Server Management CLI
This CLI subcommand deals with managing the backend FastAPI server, mainly for routine tasks
like starting the server in debug mode or generating type schemas.
"""

import os
import sys
from importlib.util import spec_from_file_location, module_from_spec
from types import ModuleType
from functools import cached_property
from pathlib import Path
from pydantic import BaseModel, Field

import typer

from config import Config
from utils import LSOFInfo



class ServerManager(BaseModel):
    config: Config = Field(default_factory=Config.load)
    root: Path = Path("./server")

    @cached_property
    def lsof(self) -> LSOFInfo:
        return LSOFInfo(port=self.config.ports["server"])

    @cached_property
    def module(self) -> ModuleType:
        spec = spec_from_file_location("server", self.root / "__init__.py")
        module = module_from_spec(spec)
        sys.modules["server"] = module
        spec.loader.exec_module(module)
        return module

    @property
    def running(self):
        return self.lsof.running
    
    def run_devserver(self):
        os.chdir(self.root)
        os.system(f"uv run fastapi dev --port {self.config.ports["server"]}")
    
    def write_model_schemas_to(self, path: Path):
        self.module.model_utils.write_schemas(
            self.module.model_utils.get_models(),
            path,
        )

manager = ServerManager()
server_app = typer.Typer()


@server_app.command("start")
def app_start():
    """
    Starts the live development server using `uv run fastapi dev` from the `server/` directory.
    """
    manager.run_devserver()


@server_app.command("status")
def app_status():
    """
    Gets the status of the development server.
    """
    if manager.running:
        print(f"App is running on {manager.lsof.port}, PID: {manager.lsof.pid}")
    else:
        print("App is not running")