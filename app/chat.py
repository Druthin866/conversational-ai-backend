import os
from groq import Groq
from models import Conversation, Message
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def process_user_message(db: Session, request):
    user_id = request.user_id
    message = request.message
    conversation_id = request.conversation_id

    # If conversation doesn't exist, create it
    if not conversation_id:
        conversation = Conversation(user_id=user_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        conversation_id = conversation.id
    else:
        conversation = db.query(Conversation).filter_by(id=conversation_id).first()
        if not conversation:
            return {"error": "Conversation not found"}

    # Save user message
    user_msg = Message(
        conversation_id=conversation_id,
        sender="user",
        text=message,
        timestamp=datetime.utcnow()
    )
    db.add(user_msg)
    db.commit()

    # Build chat history
    messages = db.query(Message).filter_by(conversation_id=conversation_id).order_by(Message.timestamp).all()
    history = "\n".join([f"{m.sender.capitalize()}: {m.text}" for m in messages])

    # Query Groq
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You're a helpful assistant for an e-commerce company."},
            {"role": "user", "content": history}
        ]
    )

    ai_response = response.choices[0].message.content

    # Save AI response
    ai_msg = Message(
        conversation_id=conversation_id,
        sender="ai",
        text=ai_response,
        timestamp=datetime.utcnow()
    )
    db.add(ai_msg)
    db.commit()

    return {
        "conversation_id": conversation_id,
        "response": ai_response
    }
