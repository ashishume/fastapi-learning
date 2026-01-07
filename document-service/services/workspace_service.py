from sqlalchemy.orm import Session
from schemas.workspace import (
    WorkspaceCreate,
    WorkspaceMembersCreate,
    WorkspaceMembersResponse,
    WorkspaceResponse,
    WorkspaceListResponse,
)
from schemas.workspace_member import WorkspaceMembersListResponse
from typing import List
from repository.workspace_repo import WorkspaceRepository
from repository.workspace_members_repo import WorkspaceMembersRepository


class WorkspaceService:
    def __init__(self, db: Session):
        self.db = db

    def create_workspace(self, workspace: WorkspaceCreate) -> WorkspaceResponse:
        workspace_repo = WorkspaceRepository(self.db)
        return workspace_repo.create_workspace(workspace)

    def get_all_workspaces(self) -> WorkspaceListResponse:
        workspace_repo = WorkspaceRepository(self.db)
        return workspace_repo.get_all_workspaces()

    def create_workspace_members(
        self, workspace_members: WorkspaceMembersCreate
    ) -> WorkspaceMembersResponse:
        workspace_members_repo = WorkspaceMembersRepository(self.db)
        return workspace_members_repo.create_workspace_members(workspace_members)

    def get_all_workspace_members(self) -> WorkspaceMembersListResponse:
        workspace_members_repo = WorkspaceMembersRepository(self.db)
        return workspace_members_repo.get_all_workspace_members()
