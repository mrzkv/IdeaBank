from pydantic import BaseModel

class IdeaInputScheme(BaseModel):
    name: str
    description: str

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