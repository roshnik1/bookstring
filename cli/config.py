from pathlib import Path
from tomllib import load
from pydantic import BaseModel, Field

from typing import Dict, Literal


class Config(BaseModel):
    """
    ### General Config
    This model tracks the static config values that may be used throughout the project.

    NOTE: Please create defaults for everything in here so that a blind `Config()`
    creates a valid config object.
    """

    ports: Dict[Literal["app", "server"], int] = Field(default_factory=dict)
    """
    Ports at which the frontend app and backend api will be served on localhost
    """

    models: Dict[Literal["schema_file"], str] = Field(default_factory=dict)
    """
    For synchronizing models between the server and app
    """

    @classmethod
    def load(cls, path: Path = Path("conf.toml")) -> "Config":
        with path.open("rb") as f:
            return Config(
                **load(f)
            )