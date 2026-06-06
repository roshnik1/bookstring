from pydantic import BaseModel, Field


class ExampleModel(BaseModel):
    name: str
    value: float

class NonModel:
    thing: str = "abc"