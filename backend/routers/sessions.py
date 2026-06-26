from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel
from typing import List
from database.config import get_db
from database.models import User

router = APIRouter(tags=["Sessions"])

class SessionCreate(BaseModel):
    title: str = "New Chat"

class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime

class MessageCreate(BaseModel):
    role: str
    content: str

class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    created_at: datetime

async def get_current_user(token: str, db: Session = Depends(get_db)):
    # Implementation similar to auth.py
    pass

@router.get("/", response_model=List[SessionResponse])
async def list_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc()).all()
    return [SessionResponse(id=session.id, user_id=session.user_id, title=session.title, created_at=session.created_at) for session in sessions]

@router.post("/", response_model=SessionResponse)
async def create_session(session_data: SessionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_session = ChatSession(id=uuid4(), user_id=current_user.id, title=session_data.title, created_at=datetime.utcnow())
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return SessionResponse(id=new_session.id, user_id=new_session.user_id, title=new_session.title, created_at=new_session.created_at)

@router.delete("/{session_id}")
async def delete_session(session_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found or not owned by user")
    db.delete(session)
    db.commit()
    return {"detail": "Session deleted successfully"}

@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def list_messages(session_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    return [MessageResponse(id=message.id, session_id=message.session_id, role=message.role, content=message.content, created_at=message.created_at) for message in messages]

@router.post("/{session_id}/messages", response_model=MessageResponse)
async def create_message(session_id: UUID, message_data: MessageCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found or not owned by user")
    new_message = ChatMessage(id=uuid4(), session_id=session.id, role=message_data.role, content=message_data.content, created_at=datetime.utcnow())
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return MessageResponse(id=new_message.id, session_id=new_message.session_id, role=new_message.role, content=new_message.content, created_at=new_message.created_at)