from pydantic import BaseModel, Field

class IdeaInputScheme(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=900)

class IdeaGetScheme(BaseModel):
    id: int
    name: str
    description: str
    creator_id: int
    status: str
    start_date: str
    end_date: str | None
    expert_id: int | None
    solution: str | None
    solution_description: str | None

class IdeaCompleteScheme(BaseModel):
    solution: str
    description: str

class NotifyScheme(BaseModel):
    id: int
    name: str
    date: str