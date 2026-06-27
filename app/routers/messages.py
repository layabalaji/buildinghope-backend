"""
Admin-only routes for the inbox: list, view-and-mark-read, toggle
read/unread, delete. Every route requires a valid admin JWT.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db import get_db
from app.models import ContactMessage
from app.schemas import ContactMessageOut, ContactMessageSummary
from app.auth import get_current_admin

router = APIRouter()


@router.get("/messages", response_model=list[ContactMessageSummary])
def list_messages(db: Session = Depends(get_db), admin: str = Depends(get_current_admin)):
    return db.query(ContactMessage).order_by(desc(ContactMessage.created_at)).all()


@router.get("/messages/{message_id}", response_model=ContactMessageOut)
def get_message(message_id: int, db: Session = Depends(get_db), admin: str = Depends(get_current_admin)):
    msg = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    if not msg.is_read:
        msg.is_read = True
        db.commit()
        db.refresh(msg)
    return msg


@router.patch("/messages/{message_id}", response_model=ContactMessageOut)
def set_read_status(message_id: int, is_read: bool, db: Session = Depends(get_db), admin: str = Depends(get_current_admin)):
    msg = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    msg.is_read = is_read
    db.commit()
    db.refresh(msg)
    return msg


@router.delete("/messages/{message_id}", status_code=204)
def delete_message(message_id: int, db: Session = Depends(get_db), admin: str = Depends(get_current_admin)):
    msg = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(msg)
    db.commit()
    return None