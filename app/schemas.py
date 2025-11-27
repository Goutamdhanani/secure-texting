from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: Optional[str] = None

class UserOut(BaseModel):
    id: int
    name: Optional[str] = None
    class Config:
        orm_mode = True

class MessageCreate(BaseModel):
    sender_id: int
    recipient_id: int
    message: str

class MessageOut(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    ciphertext: str
    nonce: str
    timestamp: datetime
    decrypted: Optional[str] = None
    class Config:
        orm_mode = True
