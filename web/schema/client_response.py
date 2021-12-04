from typing import Optional, List
from uuid import UUID

from pydantic.main import BaseModel

from web.schema.client_creation import Credits


class ClientReadResponse(BaseModel):
    id: UUID
    firstname: str
    lastname: str
    credits: Optional[List[Credits]]
