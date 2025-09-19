import datetime
import uuid
from typing import Optional

from pydantic import BaseModel
from sqlalchemy.sql.coercions import RoleImpl

from custom_type import ROLE


class IdResponse(BaseModel):
    id: int


class BaseUserRequest(BaseModel):
    name: str
    password: str


class CreateAdvRequest(BaseModel):
    title: str
    description: str
    price: int
    owner: str


class GetAdvResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
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
    price: Optional[int] = None
    owner: Optional[str] = None
    date_posted: Optional[datetime.datetime] = None

    def any(self) -> bool:
        return any(
            [self.title, self.description, self.price, self.owner, self.date_posted]
        )


class LoginRequest(BaseUserRequest):
    name: str
    password: str


class LoginResponse(BaseModel):
    token: uuid.UUID


class CreateUserRequest(BaseUserRequest):
    name: str


class CreateUserResponse(IdResponse):
    pass


class UpdateUserRequest(BaseUserRequest):
    name: Optional[str] = None
    role: Optional[int] = None
    password: Optional[str] = None


class GetUserResponse(BaseModel):
    id: int
    name: str
    passsword: str
    role: ROLE
