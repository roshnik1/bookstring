"""
# App Management CLI
This CLI subcommand deals with managing the frontend React application. Mainly for routine
tasks like launching the frontend build with HMR enabled.
"""

import os
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