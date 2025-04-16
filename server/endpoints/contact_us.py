from typing import List
from fastapi.responses import JSONResponse
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

    return JSONResponse(
            status_code=201,
            content= {
                "success":True,
                "data" : {
                    'full_name':new_contact.full_name,
                    'email':new_contact.email,
                    'phone_number':new_contact.phone_number,
                    'message':new_contact.message,
                },
                "message":'Message submitted successfully.'
            }
        )


@contact_us_router.get("", response_model=List[ContactUsOutput])
async def get_contact_us(db: Session = Depends(get_db)):
    contact_us = db.query(ContactUs).order_by(ContactUs.created_at.desc()).all()
    contact_us_list = [
        {
            'full_name':contact.full_name,
            'email':contact.email,
            'phone_number':contact.phone_number,
            'message':contact.message,
        }
        for contact in contact_us
    ]
    return JSONResponse(
            status_code=200,
            content= {
                "success":True,
                "data" : contact_us_list,
                'message':'Contact fetched successfully'
            }
            
        ) 