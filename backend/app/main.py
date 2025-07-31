from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models, schemas, chat

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/chat", response_model=schemas.ChatResponse)
def chat_endpoint(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    return chat.process_user_message(db, request)
