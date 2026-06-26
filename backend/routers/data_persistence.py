from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field
from database.models import ChatSession, ChatMessage
from database.config import get_db
from backend.services.auth import get_current_user

router = APIRouter(tags=["Data Persistence"])

# Pydantic Schemas
class ChatSessionBase(BaseModel):
    user_id: UUID
    document_id: UUID
    title: str

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionResponse(ChatSessionBase):
    id: UUID
    created_at: str
    updated_at: str

class ChatMessageBase(BaseModel):
    session_id: UUID
    role: str
    content: str
    citations: dict

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: UUID
    created_at: str

# Routes
@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
def create_chat_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
):
    new_session = ChatSession(
        user_id=current_user,
        document_id=session_data.document_id,
        title=session_data.title
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return ChatSessionResponse(
        id=new_session.id,
        user_id=new_session.user_id,
        document_id=new_session.document_id,
        title=new_session.title,
        created_at=new_session.created_at.isoformat(),
        updated_at=new_session.updated_at.isoformat()
    )

@router.get("/sessions", response_model=List[ChatSessionResponse], status_code=status.HTTP_200_OK)
def list_chat_sessions(
    db: Session = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user).all()
    return [
        ChatSessionResponse(
            id=session.id,
            user_id=session.user_id,
            document_id=session.document_id,
            title=session.title,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat()
        )
        for session in sessions
    ]

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse], status_code=status.HTTP_200_OK)
def get_chat_messages(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")
    
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
    return [
        ChatMessageResponse(
            id=message.id,
            session_id=message.session_id,
            role=message.role,
            content=message.content,
            citations=message.citations,
            created_at=message.created_at.isoformat()
        )
        for message in messages
    ]

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")
    
    db.delete(session)
    db.commit()
    return {"detail": "Chat session deleted successfully"}