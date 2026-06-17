from uuid import uuid4
import json
from pathlib import Path
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from board.task import Task, TaskStage

from typing import List, Dict, Optional, Set


class Board(BaseModel):
    stages: List[TaskStage]
    tasks: Dict[str, Task]

    @property
    def initial_stage(self) -> TaskStage:
        stages = set(self.stages)
        for stage in self.stages:
            for trans in stage.transitions:
                stages.discard(trans if isinstance(trans, TaskStage) else trans[0])
        if len(stages) == 1:
            return stages.pop()
        elif len(stages) > 1:
            raise Exception(f"Too many initial stages: {stages}")
        else:
            raise Exception("No initial stage")

    @property
    def terminal_stages(self) -> List[TaskStage]:
        return [
            stage for stage in self.stages
            if not stage.transitions
        ]

    def create(
            self,
            name: str, description: str,
            tags: Optional[Set[str]] = None,
            data: Optional[Dict] = None,
        ) -> "Task":
        return Task(
            id=uuid4(),
            name=name,
            description=description,
            tags=tags or set(),
            data=data,

            history=[(
                self.initial_stage,
                datetime.now(timezone.utc),
            )],
        )
    
    def save(self, file: Path):
        with file.open("w") as f:
            json.dump(
                {
                    "tasks": [task.model_dump_json() for task in self.tasks.values()],
                }, f,
                indent=2,
                sort_keys=True,
            )