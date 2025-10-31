from typing import Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    id: int
    email: str
    name: str
    password: str
    token: str


class RequestPayload(BaseModel):
    email: str
    name: str
    password: str
    token: str


class LoginPayload(BaseModel):
    email: str
    password: str


class ResponseModel(BaseModel):
    id: Optional[int] = None
    email: str
    name: str


class LoginResponse(BaseModel):
    message: str
    email: str
