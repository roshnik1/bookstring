from datetime import datetime
from pydantic import BaseModel, Field

from typing import List, Optional, Tuple


class ExampleModel(BaseModel):
    name: str
    value: float


class IndexedModel(BaseModel):
    id: str
    created: datetime
    archived: datetime


class Book(IndexedModel):
    name: str
    author: str
    chapters: List["Chapter"] = Field(default_factory=list)


class Chapter(IndexedModel):
    book: Book
    name: Optional[str]
    number: int


class User(BaseModel):
    name: str
    created: datetime
    archived: datetime


class UserProgress(BaseModel):
    user: User
    book: Book
    read: List[Tuple[Chapter, datetime]]


class Space(BaseModel):
    subject: IndexedModel
    creator: User


class Message(BaseModel):
    author: User
    content: str
    sent: datetime

    location: "Space | Thread"


class Node(Message):
    edits: List[Message] = Field(default_factory=list)


class Mark(BaseModel):
    user: User
    kind: str
    message: Optional[Message]


class Tag(IndexedModel):
    name: str


class Tagging(BaseModel):
    tag: Tag
    target: IndexedModel


class Thread(BaseModel):
    root: Node | Mark | Tagging