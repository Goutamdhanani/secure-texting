from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .db import SessionLocal, Base, engine
from . import crud, models, schemas

# create tables if not present (safe)
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    # in some environments (read-only DB), ignore
    pass

app = FastAPI(title="Secure Texting")

# CORS - allow all for dev. In production restrict origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Existing POST /users/ (create user)
@app.post("/users/", response_model=schemas.User)
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

# NEW: GET /users/ (list users) - fixes 405 for GET
@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_users(db, skip=skip, limit=limit)

# POST /messages/ (send message)
@app.post("/messages/", response_model=schemas.Message)
def post_message(msg: schemas.MessageCreate, db: Session = Depends(get_db)):
    return crud.send_message(db, msg)

# GET /conversations/{a}/{b}
@app.get("/conversations/{a}/{b}", response_model=list[schemas.Message])
def get_conv(a: int, b: int, db: Session = Depends(get_db)):
    return crud.get_conversation(db, a, b)
