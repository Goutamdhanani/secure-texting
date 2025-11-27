# app/main.py
from fastapi import FastAPI, Depends, Response
from sqlalchemy.orm import Session
from .db import SessionLocal, Base, engine
from . import crud, schemas
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure AES Texting App")

# Prometheus metrics
REQUEST_COUNT = Counter("app_http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Request latency seconds", ["endpoint"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# middleware-like decorator for metrics
from functools import wraps
import time

def observe(endpoint_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = fn(*args, **kwargs)
            elapsed = time.time() - start
            REQUEST_LATENCY.labels(endpoint=endpoint_name).observe(elapsed)
            # we can't always know status here; increment as 200
            REQUEST_COUNT.labels(method="GET", endpoint=endpoint_name, status="200").inc()
            return result
        return wrapper
    return decorator

@app.post("/users/")
@observe("create_user")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.post("/messages/")
@observe("send_message")
def send_message(msg: schemas.MessageCreate, db: Session = Depends(get_db)):
    return crud.send_message(db, msg)

@app.get("/conversations/{a}/{b}")
@observe("get_conversation")
def conv(a: int, b: int, db: Session = Depends(get_db)):
    return crud.get_conversation(db, a, b)

@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
