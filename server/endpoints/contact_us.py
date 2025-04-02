from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from server.endpoints.deps import get_db
from server.models.contact_us import ContactUs
from server.schemas.contact_us import ContactUsOutput, ContactUsInput

contact_us_router  = APIRouter()

@contact_us_router.post("",response_model=ContactUsOutput)
async def create_contact_us(
    payload:ContactUsInput,
    db: Session = Depends(get_db)
):
    
    new_contact = ContactUs(
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        email=payload.email,
        message=payload.message,
    )

    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    return ContactUsOutput(
        email=new_contact.email,
        full_name=new_contact.full_name,
        message=new_contact.message,
        phone_number=new_contact.phone_number
    )


@contact_us_router.get("", response_model=List[ContactUsOutput])
async def get_contact_us(db: Session = Depends(get_db)):
    bug_reports = db.query(ContactUs).order_by(ContactUs.created_at.desc()).all()
    return bug_reports