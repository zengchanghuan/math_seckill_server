from pydantic import BaseModel
from typing import List


class ProblemRequest(BaseModel):
    topic: str = "导数基础"
    difficulty: str = "基础"


class ProblemResponse(BaseModel):
    id: str
    topic: str
    difficulty: str
    question: str
    answer: str
    solution: str
    options: List[str]
    tags: List[str] = []



