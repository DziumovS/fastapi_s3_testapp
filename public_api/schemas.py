from typing import Optional
import datetime
from pydantic import BaseModel


class MemeBase(BaseModel):
    text: Optional[str] = None
    meme_name: Optional[str] = None

    class Config:
        from_attributes = True


class MemeId(MemeBase):
    image_url: Optional[str] = None
    id: int


class MemeFull(MemeId):
    date_added: datetime.datetime
    date_updated: datetime.datetime


class MemeDelete(MemeId):
    deleted: bool = True
