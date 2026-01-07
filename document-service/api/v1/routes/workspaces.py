from fastapi import APIRouter, Depends, HTTPException, status
from services.workspace_service import WorkspaceService
from database import get_db
from sqlalchemy.orm import Session
from typing import List
from schemas.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceListResponse

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new workspace",
    response_model=WorkspaceResponse,
)
def create_workspace(
    workspace: WorkspaceCreate, db: Session = Depends(get_db)
) -> WorkspaceResponse:
    try:
        workspace_service = WorkspaceService(db)
        new_workspace = workspace_service.create_workspace(workspace)
        return WorkspaceResponse.model_validate(new_workspace)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating workspace: {e}",
        )


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Get all workspaces",
    response_model=WorkspaceListResponse,
)
def get_all_workspaces(db: Session = Depends(get_db)) -> WorkspaceListResponse:
    try:
        workspace_service = WorkspaceService(db)
        workspaces = workspace_service.get_all_workspaces()
        return workspaces
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting workspaces: {e}",
        )
