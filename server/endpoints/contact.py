from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server import crud, schemas
from server.endpoints.deps import get_db
from server.utils.auth import get_current_user

contact_router = APIRouter()


def jsonify(contact):
    return {
        "first_name": contact.first_name,
        "last_name": contact.last_name,
        "user_email": contact.email,
        "user_phone_number": contact.phone_number,
        "message": contact.message,
        "created_on": str(contact.created_at),
    }


@contact_router.post(
    "/contact-us",
)
def contact_us(
    request_data: schemas.ContactBase,
    db: Session = Depends(get_db),
):

    try:
        crud.contact.create(
            db,
            obj_in=schemas.CreateContact(
                first_name=request_data.first_name,
                last_name=request_data.last_name,
                email=request_data.email,
                phone_number=request_data.phone_number,
                message=request_data.message,
            ),
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": None,
                "message": "Your request has been sent to customer care. They will contact you within the next 2 hours.",
            },
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

    finally:
        db.close()


@contact_router.get("/get-contact-us-users", status_code=status.HTTP_200_OK)
def get_user_by_contact(
    search: str = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
):
    try:

        if search:
            search = search.strip()
            contacts = crud.contact.get_search_query(db, search, skip, limit)

        else:
            contacts = crud.contact.get_contact_by_user_id(
                db, current_user.id, skip, limit
            )

        contact_count = crud.contact.get_contact_count(db, current_user.id)

        if contacts:
            user_contacts = []
            for contact in contacts:
                user = crud.user.get_by_user(db, contact.user_id)
                if user:
                    user_contacts.append(jsonify(contact))

            if not user_contacts:
                return HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No any active users are avilable.",
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "data": user_contacts,
                    "total_contacts": contact_count,
                    "error": None,
                    "message": "All contact user details fetched successfully.",
                },
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "data": [],
                    "total_contacts": 0,
                    "error": None,
                    "message": "No any user can contact with us.",
                },
            )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "data": None,
                "error": str(e.detail),
                "message": str(e.detail),
            },
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

    finally:
        db.close()
