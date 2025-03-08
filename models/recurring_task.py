from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class Source(BaseModel):
    type: str
    automation_id: str
    action_id: str
    event_id: str
    attempt: int


class CreatedBy(BaseModel):
    object: str
    id: str


class LastEditedBy(BaseModel):
    object: str
    id: str


class Parent(BaseModel):
    type: str
    database_id: str


class Text(BaseModel):
    content: str
    link: Any


class Annotations(BaseModel):
    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    code: bool
    color: str


class TitleItem(BaseModel):
    type: str
    text: Text
    annotations: Annotations
    plain_text: str
    href: Any


class Title(BaseModel):
    id: str
    type: str
    title: List[TitleItem]


class Person(BaseModel):
    email: str


class CreatedBy1(BaseModel):
    object: str
    id: str
    name: str
    avatar_url: str
    type: str
    person: Person


class Respondent(BaseModel):
    id: str
    type: str
    created_by: CreatedBy1


class SubmissionTime(BaseModel):
    id: str
    type: str
    created_time: str


class Date(BaseModel):
    start: str
    end: Any
    time_zone: Any


class StartOn(BaseModel):
    id: str
    type: str
    date: Date


class Frequency(BaseModel):
    id: str
    type: str
    number: int


class MultiSelectItem(BaseModel):
    id: str
    name: str
    color: str


class Unit(BaseModel):
    id: str
    type: str
    multi_select: List[MultiSelectItem]


class Properties(BaseModel):
    title: Title
    start_on: StartOn
    frequency: Frequency
    unit: Unit


class Data(BaseModel):
    object: str
    id: str
    created_time: str
    last_edited_time: str
    created_by: CreatedBy
    last_edited_by: LastEditedBy
    cover: Any
    icon: Any
    parent: Parent
    archived: bool
    in_trash: bool
    properties: Properties
    url: str
    public_url: Any
    request_id: str


class RecurringTask(BaseModel):
    source: Source
    data: Data
