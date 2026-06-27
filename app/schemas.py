from pydantic import BaseModel, EmailStr
from datetime import datetime


class ContactMessageCreate(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


class ContactMessageOut(BaseModel):
    id: int
    name: str
    email: str
    subject: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ContactMessageSummary(BaseModel):
    """Lighter shape for the inbox list — no full message body needed there."""
    id: int
    name: str
    subject: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True