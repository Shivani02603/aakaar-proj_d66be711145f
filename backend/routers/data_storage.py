from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field
from database.models import DocumentChunk
from database.config import get_db
from fastapi.security import OAuth2PasswordBearer

# OAuth2 dependency for JWT authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# APIRouter instance
router = APIRouter(tags=["Data Storage"])

# Pydantic schemas
class DocumentChunkBase(BaseModel):
    document_id: UUID
    chunk_index: int
    content: str
    embedding: List[float]
    metadata: dict

class DocumentChunkCreate(DocumentChunkBase):
    pass

class DocumentChunkUpdate(BaseModel):
    content: str
    embedding: List[float]
    metadata: dict

class DocumentChunkResponse(DocumentChunkBase):
    id: UUID

# Utility function for JWT authentication
def get_current_user(token: str = Depends(oauth2_scheme)):
    # Placeholder for actual JWT decoding and user validation logic
    # Replace with your authentication service logic
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")
    return {"user_id": "mock_user_id"}  # Replace with actual user retrieval logic

# Routes
@router.get("/", response_model=List[DocumentChunkResponse])
async def list_document_chunks(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    chunks = db.query(DocumentChunk).all()
    return chunks

@router.get("/{chunk_id}", response_model=DocumentChunkResponse)
async def get_document_chunk(chunk_id: UUID, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document chunk not found")
    return chunk

@router.post("/", response_model=DocumentChunkResponse, status_code=status.HTTP_201_CREATED)
async def create_document_chunk(chunk: DocumentChunkCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    new_chunk = DocumentChunk(**chunk.dict())
    db.add(new_chunk)
    db.commit()
    db.refresh(new_chunk)
    return new_chunk

@router.put("/{chunk_id}", response_model=DocumentChunkResponse)
async def update_document_chunk(chunk_id: UUID, chunk_update: DocumentChunkUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document chunk not found")
    for key, value in chunk_update.dict().items():
        setattr(chunk, key, value)
    db.commit()
    db.refresh(chunk)
    return chunk

@router.delete("/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_chunk(chunk_id: UUID, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document chunk not found")
    db.delete(chunk)
    db.commit()
    return None