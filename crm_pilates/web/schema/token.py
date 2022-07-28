from pydantic.main import BaseModel


class Token(BaseModel):
    token: str
    type: str
