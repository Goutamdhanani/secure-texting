# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .db import SessionLocal, Base, engine
from . import crud, schemas, models
from datetime import datetime
from typing import List

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure AES Texting App")

# Serve static frontend at /
app.mount("/", StaticFiles(directory="static", html=True), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.post("/messages/")
def send_message(msg: schemas.MessageCreate, db: Session = Depends(get_db)):
    # verify users exist
    if not crud.get_user(db, msg.sender_id):
        raise HTTPException(status_code=404, detail="Sender not found")
    if not crud.get_user(db, msg.recipient_id):
        raise HTTPException(status_code=404, detail="Recipient not found")
    return crud.send_message(db, msg)

# Existing conversation endpoint (raw DB rows with ciphertext)
@app.get("/conversations/raw/{a}/{b}")
def conv_raw(a: int, b: int, db: Session = Depends(get_db)):
    return crud.get_conversation(db, a, b)

# New friendly endpoint: returns decrypted plaintext for each message
@app.get("/conversations/{a}/{b}")
def conv_decrypted(a: int, b: int, db: Session = Depends(get_db)):
    # check users exist
    if not crud.get_user(db, a) or not crud.get_user(db, b):
        raise HTTPException(status_code=404, detail="One or both users not found")
    msgs = crud.get_conversation(db, a, b)
    # crud.get_conversation attached .decrypted attribute to messages
    out = []
    for m in msgs:
        out.append({
            "id": m.id,
            "sender_id": m.sender_id,
            "recipient_id": m.recipient_id,
            "message": getattr(m, "decrypted", None),
            "timestamp": m.timestamp.isoformat()
        })
    return out

@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    u = crud.get_user(db, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": u.id, "name": u.name}

@app.get("/users/{user_id}/messages")
def get_user_messages(user_id: int, db: Session = Depends(get_db)):
    if not crud.get_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    msgs = db.query(models.Message).filter(
        (models.Message.sender_id == user_id) | (models.Message.recipient_id == user_id)
    ).order_by(models.Message.timestamp.desc()).all()
    # decrypt each
    out = []
    from .crypto import decrypt_message
    for m in msgs:
        try:
            text = decrypt_message(m.ciphertext, m.nonce)
        except Exception:
            text = None
        out.append({
            "id": m.id,
            "sender_id": m.sender_id,
            "recipient_id": m.recipient_id,
            "message": text,
            "timestamp": m.timestamp.isoformat()
        })
    return out
