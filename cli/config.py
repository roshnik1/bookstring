from pathlib import Path
from tomllib import load
from pydantic import BaseModel, Field

from typing import Dict, List, Literal, Optional


class DocsConf(BaseModel):
    """
    ### Documentation Config
    Configuration for documentation generation.
    """

    class KnownDirectory(BaseModel):
        """
        ### Directory to Document
        Directories marked here are 'known' to the documentation generator and will be used
        as sources for the docgen process.
        """

        dir: Path
        """ The specific directory (relative to project root) to target for docgen """

        lang: Optional[Literal["ts", "py"]] = None
        """
        The language the directory code is any ([t]ype[s]cript or [py]thon, leave blank
        for directories without code that may have markdown or data files).
        """

        category: Literal["website", "meta"]
        """
        The basic role/category of the directory; 'website' refers to those involved in
        the Bookstring website itself and 'meta' refers to those involved in managing
        this project.
        """

    output_dir: Path
    """ Where to write out the generated XML docs """

    root_name: str
    """ Name of the 'root' document """

    known: List[KnownDirectory]
    """ Known directories to target for document generation """


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

    docs: DocsConf
    """
    For controlling how documentation generation works
    """

    @classmethod
    def load(cls, path: Path = Path("project/conf.toml")) -> "Config":
        with path.open("rb") as f:
            return Config(
                **load(f)
            )