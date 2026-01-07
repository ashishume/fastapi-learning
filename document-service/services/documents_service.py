from sqlalchemy.orm import Session
from typing import List
from typing import Dict, Any
from repository.documents_repo import DocumentsRepository
from models.document import Document
import logging
from schemas.document import DocumentListResponse

logger = logging.getLogger(__name__)


class DocumentsService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_documents(self) -> DocumentListResponse:
        documents_repo = DocumentsRepository(self.db)
        return documents_repo.get_all_documents()
