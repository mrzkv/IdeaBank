from pydantic import BaseModel

class ChatGetScheme(BaseModel):
    id: int
    idea_id: int
    status: str