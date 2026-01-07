from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List


class WorkspaceMembersCreate(BaseModel):
    workspace_id: UUID
    user_id: UUID


class WorkspaceMembersResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    workspace_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class WorkspaceMembersListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    workspace_members: List[WorkspaceMembersResponse]
