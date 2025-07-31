import os
import requests
from sqlalchemy.orm import Session
from .models import ChatSession, Message

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

def generate_ai_response(prompt: str) -> str:
    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(GROQ_API_URL, headers=HEADERS, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def process_user_message(db: Session, request):
    # Get or create session
    if request.conversation_id:
        session = db.query(ChatSession).filter(ChatSession.id == request.conversation_id).first()
    else:
        session = ChatSession(user_id=request.user_id)
        db.add(session)
        db.commit()
        db.refresh(session)

    # Save user message
    user_msg = Message(
        session_id=session.id,
        sender="user",
        message=request.message
    )
    db.add(user_msg)
    db.commit()

    # Get AI response
    ai_response = generate_ai_response(request.message)

    # Save AI response
    ai_msg = Message(
        session_id=session.id,
        sender="ai",
        message=ai_response
    )
    db.add(ai_msg)
    db.commit()

    return {
        "conversation_id": session.id,
        "user_message": request.message,
        "ai_response": ai_response
    }
