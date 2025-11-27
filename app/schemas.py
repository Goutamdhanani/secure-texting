from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base user fields
class UserBase(BaseModel):
    name: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    # Pydantic v2: allow creating model from ORM objects (from_attributes)
    model_config = {"from_attributes": True}

# Base message fields
class MessageBase(BaseModel):
    sender_id: int
    recipient_id: int

class MessageCreate(MessageBase):
    message: str

class Message(MessageBase):
    id: int
    ciphertext: Optional[str] = None
    nonce: Optional[str] = None
    timestamp: Optional[datetime] = None
    decrypted: Optional[str] = None

    model_config = {"from_attributes": True}
