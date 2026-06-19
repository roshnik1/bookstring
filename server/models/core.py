from pydantic import BaseModel, Field


class ExampleModel(BaseModel):
    """
    Just an example of a model
    """

    name: str
    """ This is a name! """

    value: float
    """ This is a value! """

    def checkmethod(self, num: int) -> float:
        return self.value + num

class NonModel:
    """
    This one isn't a model
    """
    thing: str = "abc"