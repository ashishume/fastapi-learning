import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from services.documents_service import DocumentsService
from schemas.document import DocumentCreate, DocumentResponse, DocumentListResponse
from repository.documents_repo import DocumentsRepository
from typing import List

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new document",
    response_model=Any,
)
def create_document(
    document: DocumentCreate, db: Session = Depends(get_db)
) -> DocumentResponse:
    documents_repo = DocumentsRepository(db)
    new_document = documents_repo.create_document(document)
    return new_document


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Get all documents",
    response_model=Any,
)
def get_all_documents(db: Session = Depends(get_db)) -> DocumentListResponse:
    try:
        documents_repo = DocumentsRepository(db)
        return documents_repo.get_all_documents()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting documents: {e}",
        )
