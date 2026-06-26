from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from database.models import User
from database.config import get_db
from pydantic import BaseModel
from typing import List

router = APIRouter(tags=["Users"])

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    created_at: str

async def get_current_user(token: str, db: Session = Depends(get_db)):
    # Implementation similar to auth.py
    pass

@router.get("/", response_model=List[UserResponse])
async def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [UserResponse(id=user.id, username=user.username, email=user.email, created_at=user.created_at.isoformat()) for user in users]

@router.get("/{id}", response_model=UserResponse)
async def get_user(id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(id=user.id, username=user.username, email=user.email, created_at=user.created_at.isoformat())

@router.put("/{id}", response_model=UserResponse)
async def update_user(id: UUID, user_data: UserResponse, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.username = user_data.username
    user.email = user_data.email
    db.commit()
    db.refresh(user)
    return UserResponse(id=user.id, username=user.username, email=user.email, created_at=user.created_at.isoformat())

@router.delete("/{id}")
async def delete_user(id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}