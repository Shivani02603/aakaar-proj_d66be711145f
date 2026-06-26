import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database.models import Document, User
from database.config import get_db


class DocumentManagementService:
    @staticmethod
    def create_document(
        user_id: uuid.UUID,
        filename: str,
        file_size: int,
        status: str,
        db: Session = Depends(get_db),
    ) -> Document:
        try:
            new_document = Document(
                id=uuid.uuid4(),
                user_id=user_id,
                filename=filename,
                file_size=file_size,
                status=status,
                uploaded_at=datetime.utcnow(),
                processed_at=None,
            )
            db.add(new_document)
            db.commit()
            db.refresh(new_document)
            return new_document
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating document: {str(e)}")

    @staticmethod
    def get_document_by_id(document_id: uuid.UUID, db: Session = Depends(get_db)) -> Document:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document

    @staticmethod
    def list_documents(user_id: uuid.UUID, db: Session = Depends(get_db)) -> List[Document]:
        documents = db.query(Document).filter(Document.user_id == user_id).all()
        return documents

    @staticmethod
    def update_document(
        document_id: uuid.UUID,
        filename: Optional[str] = None,
        file_size: Optional[int] = None,
        status: Optional[str] = None,
        processed_at: Optional[datetime] = None,
        db: Session = Depends(get_db),
    ) -> Document:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        if filename is not None:
            document.filename = filename
        if file_size is not None:
            document.file_size = file_size
        if status is not None:
            document.status = status
        if processed_at is not None:
            document.processed_at = processed_at

        try:
            db.commit()
            db.refresh(document)
            return document
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating document: {str(e)}")

    @staticmethod
    def delete_document(document_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        try:
            db.delete(document)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")