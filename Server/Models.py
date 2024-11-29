from pydantic import BaseModel

class User(BaseModel):
    id: str
    password: str

class Token(BaseModel):
    acces_token: str
    tip_token: str
