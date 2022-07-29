from typing import Optional, List
from uuid import UUID

from pydantic import validator
from pydantic.main import BaseModel

from crm_pilates.web.schema.client_schemas import Credits


class CreditsRead(Credits):
    @validator("value")
    def credit_must_be_positive(cls, v):
        return v


class ClientReadResponse(BaseModel):
    id: UUID
    firstname: str
    lastname: str
    credits: Optional[List[CreditsRead]]
