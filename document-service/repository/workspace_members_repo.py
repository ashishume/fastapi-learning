from sqlalchemy.orm import Session
from schemas.workspace_member import (
    WorkspaceMembersCreate,
    WorkspaceMembersResponse,
    WorkspaceMembersListResponse,
)
from models.workspace_members import WorkspaceMembers
from fastapi import HTTPException, status
from typing import List
from sqlalchemy import select


class WorkspaceMembersRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_workspace_members(
        self, workspace_members: WorkspaceMembersCreate
    ) -> WorkspaceMembersResponse:
        try:

            if (
                self.db.query(WorkspaceMembers)
                .filter(
                    WorkspaceMembers.workspace_id == workspace_members.workspace_id,
                    WorkspaceMembers.user_id == workspace_members.user_id,
                )
                .first()
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Workspace member already exists",
                )

            new_workspace_members = WorkspaceMembers(**workspace_members.model_dump())
            self.db.add(new_workspace_members)
            self.db.commit()
            self.db.refresh(new_workspace_members)
            return WorkspaceMembersResponse.model_validate(new_workspace_members)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating workspace members: {e}",
            )

    def get_all_workspace_members(self) -> WorkspaceMembersListResponse:
        try:
            workspace_members_list = (
                self.db.execute(select(WorkspaceMembers)).scalars().all()
            )
            return WorkspaceMembersListResponse(
                workspace_members=[
                    WorkspaceMembersResponse.model_validate(workspace_member)
                    for workspace_member in workspace_members_list
                ]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting workspace members: {e}",
            )
