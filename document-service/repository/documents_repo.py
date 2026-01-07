from typing import Any, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from models.document import Document
from schemas.document import DocumentCreate, DocumentResponse, DocumentListResponse
from fastapi import HTTPException, status


class DocumentsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_document(self, document: DocumentCreate) -> DocumentResponse:
        try:
            new_document = Document(**document.model_dump())
            self.db.add(new_document)
            self.db.commit()
            self.db.refresh(new_document)
            return DocumentResponse.model_validate(new_document)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating document: {e}",
            )

    def get_all_documents(self) -> DocumentListResponse:
        try:
            document_list = self.db.execute(select(Document)).scalars().all()
            return DocumentListResponse(
                documents=[
                    DocumentResponse.model_validate(document)
                    for document in document_list
                ]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting documents: {e}",
            )
