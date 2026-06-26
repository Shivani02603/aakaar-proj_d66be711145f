import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database.models import Document, DocumentChunk
from database.config import get_db
from env import OPENAI_API_KEY
import openai
from PyPDF2 import PdfReader

class DocumentProcessingService:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting text from PDF: {str(e)}")

    @staticmethod
    def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    @staticmethod
    def generate_embeddings(text_chunks: List[str]) -> List[List[float]]:
        try:
            openai.api_key = OPENAI_API_KEY
            embeddings = []
            for chunk in text_chunks:
                response = openai.Embedding.create(
                    input=chunk,
                    model="text-embedding-3-small"
                )
                embeddings.append(response['data'][0]['embedding'])
            return embeddings
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating embeddings: {str(e)}")

    @staticmethod
    def create_document_chunks(document_id: uuid.UUID, text_chunks: List[str], embeddings: List[List[float]], db: Session) -> None:
        try:
            for index, (chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
                document_chunk = DocumentChunk(
                    id=uuid.uuid4(),
                    document_id=document_id,
                    chunk_index=index,
                    content=chunk,
                    embedding=embedding,
                    metadata={}
                )
                db.add(document_chunk)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating document chunks: {str(e)}")

    @staticmethod
    def create(file_path: str, document_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
        try:
            # Extract text from the PDF
            text = DocumentProcessingService.extract_text_from_pdf(file_path)

            # Split text into chunks
            text_chunks = DocumentProcessingService.split_text_into_chunks(text)

            # Generate embeddings for the chunks
            embeddings = DocumentProcessingService.generate_embeddings(text_chunks)

            # Create document chunks in the database
            DocumentProcessingService.create_document_chunks(document_id, text_chunks, embeddings, db)

            # Update document status to processed
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            document.status = "processed"
            document.processed_at = datetime.utcnow()
            db.commit()
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

    @staticmethod
    def get_by_id(document_id: uuid.UUID, db: Session = Depends(get_db)) -> Document:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document

    @staticmethod
    def list_all(db: Session = Depends(get_db)) -> List[Document]:
        documents = db.query(Document).all()
        return documents

    @staticmethod
    def update(document_id: uuid.UUID, updates: dict, db: Session = Depends(get_db)) -> Document:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        for key, value in updates.items():
            setattr(document, key, value)
        db.commit()
        return document

    @staticmethod
    def delete(document_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        db.delete(document)
        db.commit()