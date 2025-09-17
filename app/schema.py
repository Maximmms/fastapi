import datetime
from typing import Optional

from pydantic import BaseModel


class IdResponse(BaseModel):
    id: int


class CreateAdvRequest(BaseModel):
    title: str
    description: str
    owner: str


class GetAdvResponse(BaseModel):
    id: int
    title: str
    description: str
    owner: str
    date_posted: datetime.datetime

    class Config:
        from_attributes = True


class SearchAdvRequest(BaseModel):
    advs: list[int]


class SearchAdvResponse(BaseModel):
    advs: list[GetAdvResponse]


class UpdateAdvRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class SearchParams(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    date_posted: Optional[datetime.datetime] = None

    def any(self) -> bool:
        return any([self.title, self.description, self.owner, self.date_posted])
