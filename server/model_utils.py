import json
import inspect
from pathlib import Path
from pydantic import BaseModel

from server import models

from typing import Type, List


def get_models() -> List[Type[BaseModel]]:
    return [
        member[1] for member in inspect.getmembers(models, inspect.isclass)
        if member[1].__module__.startswith("server.models") and issubclass(member[1], BaseModel)
    ]


def write_schemas(models: List[Type[BaseModel]], path: Path):
    schemas = {}
    for model in models:
        schemas[model.__name__] = model.model_json_schema()

    with path.open("w") as f:
        json.dump(schemas, f, indent=2)
