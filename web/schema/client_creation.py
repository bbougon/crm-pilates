from pydantic import validator
from pydantic.main import BaseModel


class ClientCreation(BaseModel):
    firstname: str
    lastname: str

    @validator('firstname')
    def lastname_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('You must provide the client firstname')
        return v.title()

    @validator('lastname')
    def firstname_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('You must provide the client lastname')
        return v.title()
