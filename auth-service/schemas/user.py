from pydantic import BaseModel, Field
from uuid import UUID
from models.user import Role


class User(BaseModel):
    id: str = Field(..., description="The id of the user")
    email: str = Field(..., description="The email of the user")
    name: str = Field(..., description="The name of the user")
    password: str = Field(..., description="The password of the user")
    role: Role = Field(..., description="The role of the user")


class RequestPayload(BaseModel):
    email: str
    name: str
    password: str
    role: Role = Role.USER


class LoginPayload(BaseModel):
    email: str
    password: str


class ResponseModel(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID = Field(..., description="The id of the user")
    email: str = Field(..., description="The email of the user")
    name: str = Field(..., description="The name of the user")


class UserDetailResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID = Field(..., description="The id of the user")
    email: str = Field(..., description="The email of the user")
    name: str = Field(..., description="The name of the user")


class LoginResponse(BaseModel):
    message: str = Field(..., description="The message of the login")
    email: str = Field(..., description="The email of the user")
    id: UUID = Field(..., description="The id of the user")
    name: str = Field(..., description="The name of the user")
