from datetime import datetime
from pydantic import BaseModel, Field 

from typing import Optional, List, Tuple, Dict, Hashable, Set


class TaskStage(BaseModel, Hashable):
    name: str
    description: str
    transitions: List["TaskStage" | Tuple["TaskStage", str]] = Field(default_factory=list)

    def hash(self) -> int:
        return hash(self.name)


class Task(BaseModel):
    id: str
    name: str
    description: str
    history: List[Tuple[TaskStage, datetime, Optional[Dict[str, str]]]]

    tags: Set[str] = Field(default_dict=set)
    data: Optional[Dict] = None