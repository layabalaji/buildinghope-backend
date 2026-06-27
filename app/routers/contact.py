"""POST /contact — public endpoint. Saves the message, then fires the notification email."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ContactMessage
from app.schemas import ContactMessageCreate
from app.email_utils import send_new_message_notification

router = APIRouter()


@router.post("/contact", status_code=201)
def submit_contact_message(payload: ContactMessageCreate, db: Session = Depends(get_db)):
    new_message = ContactMessage(
        name=payload.name,
        email=payload.email,
        subject=payload.subject,
        message=payload.message,
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)  # ensures new_message.id is populated before we use it below

    send_new_message_notification(
        message_id=new_message.id,
        subject=payload.subject,
        sender_name=payload.name,
    )

    return {"status": "ok"}