from sqlalchemy.orm import Session
from schemas.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceListResponse
from typing import List
from models.workspace import Workspace
from sqlalchemy import select
from fastapi import HTTPException, status


class WorkspaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_workspace(self, workspace: WorkspaceCreate) -> WorkspaceResponse:
        try:
            if (
                self.db.query(Workspace)
                .filter(Workspace.name == workspace.name)
                .first()
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Workspace with this name already exists",
                )
            new_workspace = Workspace(**workspace.model_dump())
            self.db.add(new_workspace)
            self.db.commit()
            self.db.refresh(new_workspace)
            return new_workspace
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating workspace: {e}",
            )

    def get_all_workspaces(self) -> WorkspaceListResponse:
        try:
            workspace_list = self.db.execute(select(Workspace)).scalars().all()
            return WorkspaceListResponse(
                workspaces=[
                    WorkspaceResponse.model_validate(workspace)
                    for workspace in workspace_list
                ]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting workspaces: {e}",
            )
