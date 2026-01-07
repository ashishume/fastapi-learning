from pydantic import BaseModel, Field
from uuid import UUID
from models.user import Role
from typing import Optional


class User(BaseModel):
    id: str = Field(..., description="The id of the user")
    email: str = Field(..., description="The email of the user")
    name: str = Field(..., description="The name of the user")
    password: str = Field(..., description="The password of the user")
    role: Role = Field(..., description="The role of the user")
    workspace_id: Optional[UUID] = Field(
        ..., description="The workspace id of the user"
    )


class RequestPayload(BaseModel):
    email: str
    name: str
    password: str
    role: Role = Role.USER
    workspace_id: Optional[UUID] = Field(
        ..., description="The workspace id of the user"
    )


class LoginPayload(BaseModel):
    email: str
    password: str
    workspace_id: Optional[UUID] = Field(
        ..., description="The workspace id of the user"
    )


class ResponseModel(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID = Field(..., description="The id of the user")
    email: str = Field(..., description="The email of the user")
    name: str = Field(..., description="The name of the user")
    workspace_id: Optional[UUID] = Field(
        ..., description="The workspace id of the user"
    )


class UserDetailResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID = Field(..., description="The id of the user")
    email: str = Field(..., description="The email of the user")
    name: str = Field(..., description="The name of the user")
    workspace_id: Optional[UUID] = Field(
        ..., description="The workspace id of the user"
    )


class LoginResponse(BaseModel):
    message: str = Field(..., description="The message of the login")
    email: str = Field(..., description="The email of the user")
    id: UUID = Field(..., description="The id of the user")
    name: str = Field(..., description="The name of the user")
    workspace_id: Optional[UUID] = Field(
        ..., description="The workspace id of the user"
    )
