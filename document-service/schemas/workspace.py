from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List


class WorkspaceCreate(BaseModel):
    name: str
    description: str


class WorkspaceResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime


class WorkspaceMembersCreate(BaseModel):
    workspace_id: UUID
    user_id: UUID


class WorkspaceMembersResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class WorkspaceListResponse(BaseModel):
    workspaces: List[WorkspaceResponse]
