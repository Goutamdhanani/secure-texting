from sqlalchemy.orm import Session
from . import models, schemas, crypto

def create_user(db: Session, user: schemas.UserCreate):
    u = models.User(name=user.name)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def send_message(db: Session, msg: schemas.MessageCreate):
    ciphertext, nonce = crypto.encrypt_message(msg.message)
    m = models.Message(
        sender_id=msg.sender_id,
        recipient_id=msg.recipient_id,
        ciphertext=ciphertext,
        nonce=nonce
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

def get_conversation(db: Session, a: int, b: int):
    msgs = db.query(models.Message).filter(
        ((models.Message.sender_id == a) & (models.Message.recipient_id == b)) |
        ((models.Message.sender_id == b) & (models.Message.recipient_id == a))
    ).all()

    for msg in msgs:
        msg.decrypted = crypto.decrypt_message(msg.ciphertext, msg.nonce)

    return msgs
