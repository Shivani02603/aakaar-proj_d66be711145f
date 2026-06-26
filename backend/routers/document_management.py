from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from database.models import Document, User
from database.config import get_db
from backend.services.auth import get_current_user
from datetime import datetime

router = APIRouter(tags=["Document Management"])

# Pydantic Schemas
class DocumentBase(BaseModel):
    filename: str
    file_size: int
    status: str
    uploaded_at: datetime
    processed_at: Optional[datetime] = None

class DocumentCreate(BaseModel):
    filename: str = Field(..., example="example.pdf")
    file_size: int = Field(..., example=1024)
    status: str = Field(..., example="uploaded")

class DocumentResponse(DocumentBase):
    id: UUID
    user_id: UUID

# Routes
@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a PDF document.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed."
        )

    file_content = await file.read()
    file_size = len(file_content)
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    new_document = Document(
        id=str(uuid4()),
        user_id=current_user.id,
        filename=file.filename,
        file_size=file_size,
        status="uploaded",
        uploaded_at=datetime.utcnow(),
        processed_at=None
    )
    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return new_document

@router.get("/", response_model=List[DocumentResponse], status_code=status.HTTP_200_OK)
async def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all documents uploaded by the authenticated user.
    """
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
async def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific document by ID.
    """
    document = db.query(Document).filter(
        Document.id == str(document_id), Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    return document

@router.put("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
async def update_document(
    document_id: UUID,
    document_update: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a document's metadata.
    """
    document = db.query(Document).filter(
        Document.id == str(document_id), Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    document.filename = document_update.filename
    document.file_size = document_update.file_size
    document.status = document_update.status
    document.processed_at = datetime.utcnow() if document_update.status == "processed" else None

    db.commit()
    db.refresh(document)

    return document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a document by ID.
    """
    document = db.query(Document).filter(
        Document.id == str(document_id), Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    db.delete(document)
    db.commit()

    return {"detail": "Document deleted successfully."}