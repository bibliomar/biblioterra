from bson import ObjectId
from fastapi import Form, Body
from pydantic import BaseModel, Field, NonNegativeInt, validator, ValidationError
from .query_models import ValidTopics
from enum import Enum

# This ensures that md5 is a valid 32 hexadecimal string.
md5_reg = "^[0-9a-fA-F]{32}$"


class ValidCategories(str, Enum):
    reading = "reading"
    to_read = "to-read"
    backlog = "backlog"


class ValidEntry(BaseModel):
    # Defines how a valid book entry should look like.

    authors: str = Field(..., alias="author(s)")
    series: str | None
    title: str
    topic: ValidTopics
    md5: str = Field(..., regex=md5_reg)
    extension: str | None
    size: str | None
    language: str | None
    # Only useful for keeping track of a user's progress in a book, with epubcifi.
    progress: str | None
    category: str | None

    class Config:
        allow_population_by_field_name = True


class RemoveBooks(BaseModel):
    # This model will receive a list of md5s, and remove all the matching entries.
    md5_list: list[str] = Body(..., regex=md5_reg)


class Comment(BaseModel):
    """
    Represents a new comment:
    A comment that is yet to be identified in the database (has no ID, or responses or upvotes attached)
    """
    username: str
    rating: int | None = Field(default=None, le=5, ge=0)
    content: str


class Reply(BaseModel):
    username: str
    content: str
    comment_id: str


class IdentifiedComment(Comment):
    id: str
    attached_responses: list[dict] = Field(default=[])
    upvotes: list[str] = Field(default=[])

    class Config:
        arbitrary_types_allowed = True

    @validator("id", pre=True, always=True)
    def str_to_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        else:
            return v


class IdentifiedReply(Reply):
    id: str
    upvotes: list[str] = Field(default=[])

    class Config:
        arbitrary_types_allowed = True

    @validator("id", pre=True, always=True)
    def str_to_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        else:
            return v
