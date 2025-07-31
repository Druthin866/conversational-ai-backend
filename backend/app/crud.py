def create_conversation(db, user_id: int):
    conv = models.Conversation(user_id=user_id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv

def add_message(db, conversation_id, sender, content):
    msg = models.Message(conversation_id=conversation_id, sender=sender, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
