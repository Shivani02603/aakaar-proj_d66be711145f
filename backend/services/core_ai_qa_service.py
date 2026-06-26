import uuid
from typing import List, Optional, Dict
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.models import DocumentChunk, ChatMessage
from database.config import get_db
from env import OPENAI_API_KEY
import openai


class CoreAIQAService:
    @staticmethod
    def create_chat_message(session_id: uuid.UUID, role: str, content: str, citations: Optional[Dict], db: Session = Depends(get_db)) -> ChatMessage:
        try:
            new_message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
                citations=citations,
                created_at=datetime.utcnow()
            )
            db.add(new_message)
            db.commit()
            db.refresh(new_message)
            return new_message
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    @staticmethod
    def get_chat_message_by_id(message_id: uuid.UUID, db: Session = Depends(get_db)) -> ChatMessage:
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Chat message not found")
        return message

    @staticmethod
    def list_all_chat_messages(session_id: uuid.UUID, db: Session = Depends(get_db)) -> List[ChatMessage]:
        messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
        if not messages:
            raise HTTPException(status_code=404, detail="No chat messages found for the given session")
        return messages

    @staticmethod
    def update_chat_message(message_id: uuid.UUID, content: str, db: Session = Depends(get_db)) -> ChatMessage:
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Chat message not found")
        try:
            message.content = content
            message.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(message)
            return message
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    @staticmethod
    def delete_chat_message(message_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Chat message not found")
        try:
            db.delete(message)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    @staticmethod
    def generate_answer(user_query: str, db: Session = Depends(get_db)) -> Dict:
        try:
            # Retrieve top-5 most relevant chunks based on embeddings
            chunks = db.query(DocumentChunk).order_by(DocumentChunk.embedding.distance(user_query)).limit(5).all()
            if not chunks:
                raise HTTPException(status_code=404, detail="No relevant chunks found")

            # Prepare context for the LLM
            context = "\n".join([chunk.content for chunk in chunks])
            citations = {chunk.id: chunk.metadata for chunk in chunks}

            # Generate answer using OpenAI GPT-4 or equivalent
            openai.api_key = OPENAI_API_KEY
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Answer the following question concisely with citations: {user_query}\n\nContext:\n{context}"}
                ]
            )
            answer = response['choices'][0]['message']['content']

            return {
                "answer": answer,
                "citations": citations
            }
        except openai.error.OpenAIError as e:
            raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")