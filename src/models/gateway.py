from typing import List
from pydantic import BaseModel, Field


"""
PYDANTIC MODELS FOR INGESTION THROUGH THE API GATEWAY
"""


class Date(BaseModel):
    start: str


class StartOn(BaseModel):
    date: Date


class MultiSelectItem(BaseModel):
    name: str


class Type(BaseModel):
    multi_select: List[MultiSelectItem]


class Tag(BaseModel):
    multi_select: List[MultiSelectItem]


class Frequency(BaseModel):
    number: int


class EndOn(BaseModel):
    date: Date | None


class Unit(BaseModel):
    multi_select: List[MultiSelectItem]


class Text(BaseModel):
    content: str


class TitleItem(BaseModel):
    plain_text: str


class Title(BaseModel):
    title: List[TitleItem]


class Properties(BaseModel):
    start_on: StartOn = Field(..., alias='Start On')
    type: Type = Field(..., alias='Type')
    tag: Tag = Field(..., alias='Tag')
    frequency: Frequency = Field(..., alias='Frequency')
    end_on: EndOn = Field(..., alias='End On')
    unit: Unit = Field(..., alias='Unit')
    title: Title = Field(..., alias='Title')


class Data(BaseModel):
    id: str
    properties: Properties


class RecurringEvent(BaseModel):
    data: Data
