import uuid
from sqlalchemy.exc import SQLAlchemyError
from database.models import (
    engine,
    SessionLocal,
    User,
    Document,
    DocumentChunk,
    ChatSession,
    ChatMessage
)

def seed_database():
    session = SessionLocal()
    try:
        # Seed Users
        user1 = User(
            id=str(uuid.uuid4()),
            email="alice@example.com",
            hashed_password="hashed_password_1"
        )
        user2 = User(
            id=str(uuid.uuid4()),
            email="bob@example.com",
            hashed_password="hashed_password_2"
        )
        user3 = User(
            id=str(uuid.uuid4()),
            email="charlie@example.com",
            hashed_password="hashed_password_3"
        )
        session.add_all([user1, user2, user3])
        session.commit()

        # Seed Documents
        document1 = Document(
            id=str(uuid.uuid4()),
            user_id=user1.id,
            filename="document1.pdf",
            file_size=1024,
            status="processed",
            uploaded_at="2023-10-01 12:00:00"
        )
        document2 = Document(
            id=str(uuid.uuid4()),
            user_id=user2.id,
            filename="document2.pdf",
            file_size=2048,
            status="uploaded",
            uploaded_at="2023-10-01 12:30:00"
        )
        document3 = Document(
            id=str(uuid.uuid4()),
            user_id=user3.id,
            filename="document3.pdf",
            file_size=512,
            status="processed",
            uploaded_at="2023-10-01 13:00:00"
        )
        session.add_all([document1, document2, document3])
        session.commit()

        # Seed DocumentChunks
        chunk1 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document1.id,
            chunk_index=0,
            content="This is the first chunk of document1.",
            embedding=[0.1] * 1536,
            metadata={"source": "document1.pdf"}
        )
        chunk2 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document1.id,
            chunk_index=1,
            content="This is the second chunk of document1.",
            embedding=[0.2] * 1536,
            metadata={"source": "document1.pdf"}
        )
        chunk3 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document2.id,
            chunk_index=0,
            content="This is the first chunk of document2.",
            embedding=[0.3] * 1536,
            metadata={"source": "document2.pdf"}
        )
        session.add_all([chunk1, chunk2, chunk3])
        session.commit()

        # Seed ChatSessions
        session1 = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user1.id,
            document_id=document1.id,
            title="Session 1",
            created_at="2023-10-01 14:00:00",
            updated_at="2023-10-01 14:30:00"
        )
        session2 = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user2.id,
            document_id=document2.id,
            title="Session 2",
            created_at="2023-10-01 15:00:00",
            updated_at="2023-10-01 15:30:00"
        )
        session3 = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user3.id,
            document_id=document3.id,
            title="Session 3",
            created_at="2023-10-01 16:00:00",
            updated_at="2023-10-01 16:30:00"
        )
        session.add_all([session1, session2, session3])
        session.commit()

        # Seed ChatMessages
        message1 = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session1.id,
            role="user",
            content="What is this document about?",
            citations=None,
            created_at="2023-10-01 14:05:00"
        )
        message2 = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session1.id,
            role="assistant",
            content="This document is about AI.",
            citations={"source": "document1.pdf"},
            created_at="2023-10-01 14:10:00"
        )
        message3 = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session2.id,
            role="user",
            content="Can you summarize this?",
            citations=None,
            created_at="2023-10-01 15:05:00"
        )
        session.add_all([message1, message2, message3])
        session.commit()

        print("Database seeded successfully.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error seeding database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_database()