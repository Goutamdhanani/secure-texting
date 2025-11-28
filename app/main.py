# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from .db import SessionLocal, Base, engine
from . import crud, schemas, models
from datetime import datetime
from typing import List

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure AES Texting App")

# -- CORS (development-friendly) --
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production to your frontend origin(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from /static so API routes are not shadowed
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve SPA index at root
@app.get("/", include_in_schema=False)
def index():
    return FileResponse("static/index.html")

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------
# API endpoints
# ------------------

@app.post("/users/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.get("/users/")
def list_users_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_users(db, skip=skip, limit=limit)

@app.post("/messages/")
def send_message(msg: schemas.MessageCreate, db: Session = Depends(get_db)):
    # verify users exist
    if not db.get(models.User, msg.sender_id):
        raise HTTPException(status_code=404, detail="Sender not found")
    if not db.get(models.User, msg.recipient_id):
        raise HTTPException(status_code=404, detail="Recipient not found")
    return crud.send_message(db, msg)

@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    u = db.get(models.User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": u.id, "name": u.name}

@app.get("/users/{user_id}/messages")
def get_user_messages(user_id: int, db: Session = Depends(get_db)):
    if not db.get(models.User, user_id):
        raise HTTPException(status_code=404, detail="User not found")

    msgs = db.query(models.Message).filter(
        (models.Message.sender_id == user_id) | (models.Message.recipient_id == user_id)
    ).order_by(models.Message.timestamp.desc()).all()

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

# -------------------------
# Contact summaries (must be BEFORE generic /conversations/{a}/{b})
# -------------------------
@app.get("/conversations/user/{user_id}")
def contact_summaries(user_id: int, db: Session = Depends(get_db)):
    if not db.get(models.User, user_id):
        raise HTTPException(status_code=404, detail="User not found")

    Message = models.Message
    User = models.User

    msgs = db.query(Message).filter(
        (Message.sender_id == user_id) | (Message.recipient_id == user_id)
    ).order_by(Message.timestamp.desc()).all()

    summaries = {}
    from .crypto import decrypt_message

    for m in msgs:
        contact_id = m.recipient_id if m.sender_id == user_id else m.sender_id
        if contact_id not in summaries:
            try:
                text = decrypt_message(m.ciphertext, m.nonce)
            except Exception:
                text = None
            contact_user = db.get(User, contact_id)
            summaries[contact_id] = {
                "contact_id": contact_id,
                "contact_name": contact_user.name if contact_user else None,
                "last_message": text,
                "last_message_time": m.timestamp.isoformat(),
                "unread_count": 0
            }

    # If Message has a 'read' column, calculate unread_count per contact
    if hasattr(Message, "read"):
        unread_counts = db.query(Message.sender_id, func.count(Message.id)).filter(
            (Message.recipient_id == user_id) & (Message.read == False)
        ).group_by(Message.sender_id).all()
        for sender_id, cnt in unread_counts:
            if sender_id in summaries:
                summaries[sender_id]["unread_count"] = cnt

    out = sorted(summaries.values(), key=lambda x: x["last_message_time"], reverse=True)
    return out

# Raw encrypted conversation
@app.get("/conversations/raw/{a}/{b}")
def conv_raw(a: int, b: int, db: Session = Depends(get_db)):
    return crud.get_conversation(db, a, b)

# Decrypted conversation (generic) - returns both `message` and `decrypted` keys
@app.get("/conversations/{a}/{b}")
def conv_decrypted(a: int, b: int, db: Session = Depends(get_db)):
    if not db.get(models.User, a) or not db.get(models.User, b):
        raise HTTPException(status_code=404, detail="One or both users not found")

    msgs = crud.get_conversation(db, a, b)

    out = []
    for m in msgs:
        decrypted_text = getattr(m, "decrypted", None)
        out.append({
            "id": m.id,
            "sender_id": m.sender_id,
            "recipient_id": m.recipient_id,
            # keep legacy key "message" for older clients
            "message": decrypted_text,
            # also include explicit "decrypted" (frontend expects this)
            "decrypted": decrypted_text,
            "timestamp": m.timestamp.isoformat()
        })
    return out

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}

# Mark conversation read (best-effort)
@app.post("/conversations/{user_id}/{contact_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_conversation_read(user_id: int, contact_id: int, db: Session = Depends(get_db)):
    if not db.get(models.User, user_id) or not db.get(models.User, contact_id):
        raise HTTPException(status_code=404, detail="User or contact not found")

    Message = models.Message
    if hasattr(Message, "read"):
        db.query(Message).filter(
            (Message.sender_id == contact_id) & (Message.recipient_id == user_id) & (Message.read == False)
        ).update({Message.read: True})
        db.commit()

    return None
