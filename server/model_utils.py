import json
import inspect
from pathlib import Path
from pydantic import BaseModel
from pydantic.json_schema import models_json_schema

from server import models

from typing import Type, List


def get_models() -> List[Type[BaseModel]]:
    return [
        member[1] for member in inspect.getmembers(models, inspect.isclass)
        if member[1].__module__.startswith("server.models") and issubclass(member[1], BaseModel)
    ]


def write_schemas(models: List[Type[BaseModel]], path: Path):
    _, schemas = models_json_schema(
        [(model, "validation") for model in models],
        ref_template="#/components/schemas/{model}"
    )

    openapi_document = {
        "openapi": "3.1.0",
        "info": {
            "title": "BookString API Schema",
            "version": "0.0.0",
        },
        "paths": {},
        "components": {
            "schemas": schemas.get("$defs", schemas),
        }
    }

    with path.open("w") as f:
        json.dump(openapi_document, f, indent=2)
