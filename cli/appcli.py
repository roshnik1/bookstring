"""
# App Management CLI
This CLI subcommand deals with managing the frontend React application. Mainly for routine
tasks like launching the frontend build with HMR enabled.
"""

import os
from subprocess import run
from functools import cached_property
from pathlib import Path
from pydantic import BaseModel, Field

import typer

from config import Config
from utils import LSOFInfo


class ApplicationManager(BaseModel):
    config: Config = Field(default_factory=Config.load)
    root: Path = Path("./app")

    @cached_property
    def lsof(self) -> LSOFInfo:
        return LSOFInfo(port=self.config.ports["app"])

    @property
    def running(self):
        return self.lsof.running
    
    def run_devserver(self):
        os.chdir(self.root)
        os.system(f"deno run dev --port {self.config.ports["app"]}")
    
    def build_types(self, schema_def: Path, type_def: Path):
        """
        Use [openapi-typescript](https://openapi-ts.dev) to generate type definitions from a schema
        """
        os.chdir(self.root)
        run([
            "deno", "run",
            "--allow-env", "--allow-read", "--allow-write",
            "npm:openapi-typescript",
            str(schema_def),
            "-o", str(type_def),
        ])

manager = ApplicationManager()
app_app = typer.Typer()


@app_app.command("start")
def app_start():
    """
    Starts the live development server using `deno run dev` from the `app/` directory.
    """
    manager.run_devserver()


@app_app.command("status")
def app_status():
    """
    Gets the status of the development server.
    """
    if manager.running:
        print(f"App is running on {manager.lsof.port}, PID: {manager.lsof.pid}")
    else:
        print("App is not running")