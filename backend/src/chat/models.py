from pydantic import BaseModel
from typing import List

class ChatGetScheme(BaseModel):
    chat_id: int
    idea_id: int
    interlocutors_ids: List[int]
    chat_status: str
    idea_status: str

class MessageSendScheme(BaseModel):
    msg: str

class ChatsMessageScheme(BaseModel):
    msg: str
    its_your_msg: bool
