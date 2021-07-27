from uuid import UUID

from pydantic.main import BaseModel


class ClientReadResponse(BaseModel):
    id: UUID
    firstname: str
    lastname: str