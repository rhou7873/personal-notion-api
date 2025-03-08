from typing import List
from pydantic import BaseModel, Field


"""
PYDANTIC MODELS FOR INGESTION THROUGH THE API GATEWAY
"""


class Frequency(BaseModel):
    number: int


class MultiSelectItem(BaseModel):
    name: str


class Unit(BaseModel):
    multi_select: List[MultiSelectItem]


class Date(BaseModel):
    start: str


class StartOn(BaseModel):
    date: Date


class Text(BaseModel):
    content: str


class TitleItem(BaseModel):
    plain_text: str


class Title(BaseModel):
    title: List[TitleItem]


class Tag(BaseModel):
    multi_select: List[MultiSelectItem]


class Select(BaseModel):
    name: str


class Type(BaseModel):
    select: Select


class EndOn(BaseModel):
    date: Date | None


class Properties(BaseModel):
    frequency: Frequency = Field(..., alias="Frequency")
    unit: Unit = Field(..., alias="Unit")
    start_on: StartOn = Field(..., alias="Start On")
    title: Title = Field(..., alias="Title")
    tag: Tag = Field(..., alias="Tag")
    type: Type = Field(..., alias="Type")
    end_on: EndOn = Field(..., alias="End On")


class Data(BaseModel):
    id: str
    properties: Properties


class RecurringEvent(BaseModel):
    data: Data
