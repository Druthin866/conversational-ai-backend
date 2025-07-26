from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models
from .database import SessionLocal, engine
from datetime import datetime

app = FastAPI()

# Create tables on startup
models.Base.metadata.create_all(bind=engine)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/chat")
def chat(user_message: str, user_id: int, conversation_id: int = None, db: Session = Depends(get_db)):
    # 1. If no conversation_id is provided, create a new ChatSession
    if conversation_id is None:
        session = models.ChatSession(user_id=user_id)
        db.add(session)
        db.commit()
        db.refresh(session)
    else:
        session = db.query(models.ChatSession).filter_by(id=conversation_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Conversation not found")

    # 2. Save user's message
    user_msg = models.Message(
        session_id=session.id,
        sender="user",
        message=user_message,
        timestamp=datetime.utcnow()
    )
    db.add(user_msg)

    # 3. Generate placeholder AI response
    ai_response = "This is a placeholder AI response."  # Will be replaced in Milestone 5

    # 4. Save AI's response
    ai_msg = models.Message(
        session_id=session.id,
        sender="ai",
        message=ai_response,
        timestamp=datetime.utcnow()
    )
    db.add(ai_msg)

    db.commit()

    return {
        "conversation_id": session.id,
        "user_message": user_message,
        "ai_response": ai_response
    }
