import os
import requests
from models import Conversation, Message, User
from sqlalchemy.orm import Session

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
    # Get or create conversation
    if request.conversation_id:
        conversation = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
    else:
        conversation = Conversation(user_id=request.user_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        sender="user",
        message=request.message
    )
    db.add(user_msg)
    db.commit()

    # Generate AI response
    ai_response = generate_ai_response(request.message)

    # Save AI message
    ai_msg = Message(
        conversation_id=conversation.id,
        sender="ai",
        message=ai_response
    )
    db.add(ai_msg)
    db.commit()

    return {
        "conversation_id": conversation.id,
        "user_message": request.message,
        "ai_response": ai_response
    }
