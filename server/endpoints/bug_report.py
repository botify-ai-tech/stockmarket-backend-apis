import os
import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from server.endpoints.deps import get_db
from fastapi.responses import JSONResponse
from server.models.bug_report import BugReport
from server.schemas.bug_report import BugReportOutput
from fastapi import  File, UploadFile, Form, Depends


bug_report_router  = APIRouter()

@bug_report_router.post("",response_model=BugReportOutput)
async def create_bug_report(
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    full_name: Optional[str] = Form(None),
    message: str = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    
    # create photo_path
    photo_path = None

    if photo:
        # Generate unique filename
        file_extension = os.path.splitext(photo.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        photo_path = os.path.join("static", unique_filename)
        with open(photo_path, "wb") as buffer:
            buffer.write(await photo.read())
    try:
    # create bug_report 
        new_bug_report = BugReport(
            email = email,
            phone = phone,
            full_name = full_name,
            message= message,
            photo=photo_path
        )
        db.add(new_bug_report)
        db.commit()
        db.refresh(new_bug_report)
        # return BugReportOutput(
        #     phone=new_bug_report.phone,
        #     email=new_bug_report.email,
        #     full_name=new_bug_report.full_name,
        #     message=new_bug_report.message,
        #     photo=new_bug_report.photo
        # )

        return JSONResponse(
            status_code=201,
            content= {
                "success":True,
                "data" : {
                    'phone':new_bug_report.phone,
                    'email':new_bug_report.email,
                    'full_name':new_bug_report.full_name,
                    'message':new_bug_report.message,
                    'photo':new_bug_report.photo
                },
                "message":'bug report created'
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )

@bug_report_router.get("", response_model=List[BugReportOutput])
async def get_bug_reports(db: Session = Depends(get_db)):
    bug_reports = db.query(BugReport).order_by(BugReport.created_at.desc()).all()
    bug_reports_list = [
        {
            'phone': bug.phone,
            'email': bug.email,
            'full_name': bug.full_name,
            'message': bug.message,
            'photo': bug.photo
        }
        for bug in bug_reports
    ]
    return JSONResponse(
            status_code=201,
            content= {
                "success":True,
                "data" : bug_reports_list,
                'message':'bug reports fetched!'
            }
            
        ) 