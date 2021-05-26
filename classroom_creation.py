from pydantic import BaseModel

class ClassroomCreation(BaseModel):

    name:str
    hour:str