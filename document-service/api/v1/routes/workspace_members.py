from fastapi import APIRouter, Depends, status, HTTPException
from schemas.workspace_member import (
    WorkspaceMembersCreate,
    WorkspaceMembersResponse,
    WorkspaceMembersListResponse,
)
from database import get_db
from sqlalchemy.orm import Session
from services.workspace_service import WorkspaceService
from typing import List

router = APIRouter()


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=WorkspaceMembersResponse
)
def create_workspace_member(
    workspace_member: WorkspaceMembersCreate, db: Session = Depends(get_db)
) -> WorkspaceMembersResponse:
    try:
        workspace_service = WorkspaceService(db)
        return workspace_service.create_workspace_members(workspace_member)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating workspace member: {e}",
        )


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Get all workspace members",
    response_model=WorkspaceMembersListResponse,
)
def get_all_workspace_members(
    db: Session = Depends(get_db),
) -> WorkspaceMembersListResponse:
    workspace_service = WorkspaceService(db)
    return workspace_service.get_all_workspace_members()
