from pydantic.main import BaseModel


class ClientCreation(BaseModel):
    firstname: str
    lastname: str
