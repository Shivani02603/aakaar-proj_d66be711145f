from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from database.models import Document, DocumentChunk
from database.config import get_db
from backend.services.document_processing_service import (
    extract_text_from_pdf,
    split_text_into_chunks,
    generate_embeddings,
)
from backend.services.auth import get_current_user

router = APIRouter(tags=["Document Processing"])

# Pydantic Schemas
class DocumentChunkBase(BaseModel):
    document_id: UUID
    chunk_index: int
    content: str
    embedding: Optional[List[float]] = None
    metadata: Optional[dict] = None

class DocumentChunkResponse(DocumentChunkBase):
    id: UUID

class DocumentProcessingResponse(BaseModel):
    document_id: UUID
    chunks: List[DocumentChunkResponse]

# Routes
@router.post("/process", response_model=DocumentProcessingResponse)
async def process_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Process an uploaded document: extract text, split into chunks, and generate embeddings.
    """
    try:
        # Extract text from the uploaded PDF
        extracted_text = extract_text_from_pdf(file.file)

        # Split text into overlapping chunks
        chunks = split_text_into_chunks(extracted_text, chunk_size=1000, overlap=200)

        # Generate embeddings for each chunk
        processed_chunks = []
        for index, chunk in enumerate(chunks):
            embedding = generate_embeddings(chunk)
            document_chunk = DocumentChunk(
                document_id=None,  # Placeholder, will be updated later
                chunk_index=index,
                content=chunk,
                embedding=embedding,
                metadata=None,
            )
            db.add(document_chunk)
            db.commit()
            db.refresh(document_chunk)
            processed_chunks.append(document_chunk)

        # Create response
        response = DocumentProcessingResponse(
            document_id=None,  # Placeholder, will be updated later
            chunks=[
                DocumentChunkResponse(
                    id=chunk.id,
                    document_id=chunk.document_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    embedding=chunk.embedding,
                    metadata=chunk.metadata,
                )
                for chunk in processed_chunks
            ],
        )
        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the document: {str(e)}",
        )

@router.get("/chunks", response_model=List[DocumentChunkResponse])
async def list_document_chunks(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all chunks for a given document.
    """
    try:
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No chunks found for the specified document.",
            )
        return [
            DocumentChunkResponse(
                id=chunk.id,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                embedding=chunk.embedding,
                metadata=chunk.metadata,
            )
            for chunk in chunks
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving document chunks: {str(e)}",
        )

@router.get("/chunks/{chunk_id}", response_model=DocumentChunkResponse)
async def get_document_chunk(
    chunk_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieve a specific document chunk by ID.
    """
    try:
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document chunk not found.",
            )
        return DocumentChunkResponse(
            id=chunk.id,
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            embedding=chunk.embedding,
            metadata=chunk.metadata,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the document chunk: {str(e)}",
        )

@router.delete("/chunks/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_chunk(
    chunk_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a specific document chunk by ID.
    """
    try:
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document chunk not found.",
            )
        db.delete(chunk)
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the document chunk: {str(e)}",
        )