from typing import Optional, List

from pydantic import validator
from pydantic.main import BaseModel

from domain.classroom.classroom_type import ClassroomSubject


class Credits(BaseModel):
    value: int
    subject: ClassroomSubject


class ClientCreation(BaseModel):
    firstname: str
    lastname: str
    credits: Optional[List[Credits]]

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
