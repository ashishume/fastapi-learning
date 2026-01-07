from sqlalchemy.orm import Session
from schemas.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceListResponse
from typing import List
from repository.workspace_repo import WorkspaceRepository


class WorkspaceService:
    def __init__(self, db: Session):
        self.db = db

    def create_workspace(self, workspace: WorkspaceCreate) -> WorkspaceResponse:
        workspace_repo = WorkspaceRepository(self.db)
        return workspace_repo.create_workspace(workspace)

    def get_all_workspaces(self) -> WorkspaceListResponse:
        workspace_repo = WorkspaceRepository(self.db)
        return workspace_repo.get_all_workspaces()
