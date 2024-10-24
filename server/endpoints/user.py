from datetime import datetime
import json
import random

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
import firebase_admin
from sqlalchemy.orm import Session

from server import crud, schemas
from server.utils.auth import (
    authenticate_user,
    get_current_user,
    get_password_hash,
    get_validate_refresh_token,
    jwt_access_token,
    jwt_refresh_token,
    refresh_to_access_token,
    verify_pass_toekn,
    verify_password,
)
from server.utils.common import validate_email_send_otp
from firebase_admin import credentials, auth
from server.endpoints.deps import get_db


cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)

user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.post(
    "/login",
)
async def login_for_access_token(
    data: schemas.LoginInput, db: Session = Depends(get_db)
):
    try:
        user = authenticate_user(db, data.email, data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.providers == json.dumps(["google.com"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please login with google.",
            )

        user_account = crud.user.verify_user(db, data.email)
        if not user_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your aacount has been deleted, Please sign up again.",
            )

        access_token = jwt_access_token(data={"sub": user.email, "id": user.id})

        refresh_token = jwt_refresh_token(data={"sub": user.email, "id": user.id})
        response = schemas.RespUser(
            id=user.id,
            email=user.email,
            username=user.username,
            avatar=user.avatar,
            is_verified=user.is_verified,
            providers=user.providers,
            role=user.role,
            firebase_id=user.firebase_id,
            is_social=user.is_social,
            device=user.device,
            created_at=str(user.created_at),
            updated_at=str(user.updated_at),
            token=schemas.Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            ),
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": response.dict(),
                "message": "You have successfully logged in.",
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


@user_router.post("/profile", response_model=schemas.UserProfile)
async def get_profile(current_user=Depends(get_current_user)):
    try:
        profile = schemas.UserProfile(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            avatar=current_user.avatar,
            role=current_user.role,
            device=current_user.device,
            is_social=current_user.is_social,
        )
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": profile.dict(),
                "message": "User profile fetched successfully.",
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


@user_router.post("/signup")
async def sign_up(data: schemas.UserCreateInput, db: Session = Depends(get_db)):
    try:
        username = data.username
        email = data.email.lower().strip()
        user = crud.user.get_by_email(db, email=email)

        if user:
            if user.is_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You already have an account with us. please continue with login.",
                )
        else:
            hashed_password = get_password_hash(data.password)
            user = crud.user.create(
                db,
                obj_in=schemas.UserBase(
                    username=username, email=data.email, hashed_password=hashed_password, device=data.device
                ),
            )
        otp = str(random.randint(99999, 999999))
        otp_sent = await validate_email_send_otp(db, email, user.id, key=otp)
        if otp_sent:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "error": None,
                    "data": None,
                    "message": "OTP sent to your email, please verify your email to continue.",
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


@user_router.post("/verify-otp")
async def verify_otp(data: schemas.VerifyOTP, db: Session = Depends(get_db)):
    try:
        email = data.email.lower().strip()
        otp_sent = data.otp.lower().strip()

        email_otp_obj = crud.email_otp.get_by_email(db, email=email)
        user_obj = crud.user.get_by_email(db, email=email)

        if user_obj:
            if user_obj.is_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Your email is already verified.",
                )

        if not email_otp_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="First proceed via sending OTP request.",
            )

        otp = email_otp_obj.otp
        time_now = datetime.utcnow()

        if (((time_now - email_otp_obj.updated_at).total_seconds()) / 60) < 2:
            if str(otp_sent) == str(otp):
                user_obj = crud.user.update(
                    db,
                    db_obj=user_obj,
                    obj_in=schemas.UserUpdate(is_verified=True, is_active=True),
                )

                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "error": None,
                        "data": None,
                        "message": "OTP verified successfully, Please login.",
                    },
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="OTP mismatched, Please provide correct OTP.",
                )
        else:
            crud.email_otp.remove(db, id=email_otp_obj.id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP is expired, please proceed new OTP.",
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


@user_router.post("/resend-otp")
async def resend_otp(data: schemas.EmailSchema, db: Session = Depends(get_db)):
    try:
        email = data.email.lower().strip()
        user_obj = crud.user.get_by_email(db, email=email)
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="First proceed via sending OTP request.",
            )

        if user_obj and user_obj.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your email is already verified.",
            )
        if data.type == "sign_up":
            otp = str(random.randint(99999, 999999))
            otp_sent = await validate_email_send_otp(db, email, user_obj.id, key=otp)
        else:
            otp_sent = await validate_email_send_otp(db, email, user_obj.id, key=None)
        if otp_sent:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "error": None,
                    "data": None,
                    "message": "OTP sent to your email, please verify your email to continue.",
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


@user_router.post("/change-password")
async def change_password(
    data: schemas.ChangePassword,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        old_password = data.old_password
        new_password = data.new_password
        user_obj = crud.user.get_by_email(db, email=current_user.email)
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User not found."
            )

        if old_password == new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password and new password are same.",
            )

        if not verify_password(old_password, user_obj.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password is incorrect.",
            )

        hashed_password = get_password_hash(new_password)
        user_obj = crud.user.update(
            db,
            db_obj=user_obj,
            obj_in=schemas.UserUpdate(hashed_password=hashed_password),
        )
        # access_token_expires = timedelta(minutes=TOKEN_EXPIRE_DELTA)
        access_token = jwt_access_token(data={"sub": user_obj.email, "id": user_obj.id})

        refresh_token = jwt_refresh_token(
            data={"sub": user_obj.email, "id": user_obj.id}
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                },
                "message": "Password changed successfully.",
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


@user_router.post("/forgot-password")
async def forgot_password_send_otp(
    data: schemas.EmailSchema, db: Session = Depends(get_db)
):
    try:
        email = data.email.lower().strip()
        user_obj = crud.user.get_by_email(db, email=email)
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User not found."
            )

        otp_sent = await validate_email_send_otp(db, email, user_obj.id, key=None)
        if otp_sent:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "error": None,
                    "data": None,
                    "message": "Please check your email. You have received a link to reset your password.",
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


@user_router.post("/reset-forgot-password")
async def reset_forgot_password(
    token: str, data: schemas.ResetPassword, db: Session = Depends(get_db)
):
    try:
        verify_token = verify_pass_toekn(db=db, token=token)
        id = verify_token.id
        user = crud.user.get_by_id(db, id=id)
        if user:
            email = user.email
            if not email == data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Please provide a valid email address. Your email is not registered on our website.",
                )

            new_password = data.new_password

            hashed_password = get_password_hash(new_password)
            crud.user.update(
                db,
                db_obj=user,
                obj_in=schemas.UserUpdate(hashed_password=hashed_password),
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "error": None,
                    "data": None,
                    "message": "Your password has been successfully reset. Please log in with your new credentials.",
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


@user_router.post("/update-profile")
async def update_profile(
    data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        user_obj = crud.user.get_by_email(db, email=current_user.email)
        if not user_obj:
            raise HTTPException(400, "User not found.")

        user_obj = crud.user.update(db, db_obj=user_obj, obj_in=data)
        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "Profile updated successfully."},
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


@user_router.post("/refresh-token")
async def refresh_toekn(
    current_user=Depends(get_validate_refresh_token), db: Session = Depends(get_db)
):
    try:

        access_token = refresh_to_access_token(current_user)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": {
                    "access_token": access_token,
                    "token_type": "bearer",
                },
                "message": "Access token generated successfully.",
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


@user_router.post("/google")
def google(
    request_data: schemas.GoogleAuthSchema,
    db: Session = Depends(get_db),
):
    google_user_info = auth.verify_id_token(request_data.token, clock_skew_seconds=10)

    firebase_id = google_user_info["uid"]
    email = google_user_info["email"]
    user = crud.user.get_by_email(db, email=email)

    if not user:
        user = crud.user.create(
            db,
            obj_in=schemas.UserBase(
                username=google_user_info["name"],
                email=email,
                is_verified=True,
                is_active=True,
                providers=json.dumps(["google.com"]),
                firebase_id=firebase_id,
                is_social=True,
                device=request_data.device,
            ),
        )

        access_token = jwt_access_token(data={"sub": user.email, "id": user.id})

        refresh_token = jwt_refresh_token(data={"sub": user.email, "id": user.id})

        response = schemas.RespUser(
            id=user.id,
            email=user.email,
            username=user.username,
            avatar=user.avatar,
            is_verified=user.is_verified,
            providers=user.providers,
            role=user.role,
            firebase_id=user.firebase_id,
            is_social=user.is_social,
            device=user.device,
            created_at=str(user.created_at),
            updated_at=str(user.updated_at),
            token=schemas.Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            ),
        )
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": response.dict(),
                "message": "You have successfully Sign up.",
            },
        )

    else:
        if user.is_social:
            user = crud.user.update(
                db,
                db_obj=user,
                obj_in=schemas.UserUpdate(is_verified=True, is_active=True),
            )

            access_token = jwt_access_token(data={"sub": user.email, "id": user.id})

            refresh_token = jwt_refresh_token(data={"sub": user.email, "id": user.id})

            response = schemas.RespUser(
                id=user.id,
                email=user.email,
                username=user.username,
                avatar=user.avatar,
                is_verified=user.is_verified,
                providers=user.providers,
                role=user.role,
                firebase_id=user.firebase_id,
                is_social=user.is_social,
                device=user.device,
                created_at=str(user.created_at),
                updated_at=str(user.updated_at),
                token=schemas.Token(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type="bearer",
                ),
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "error": None,
                    "data": response.dict(),
                    "message": "You have successfully logged in.",
                },
            )


@user_router.delete("/delete-account")
def delete_account(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = crud.user.get_by_user(db, id=current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user found.",
        )

    crud.user.update(
        db, db_obj=user, obj_in=schemas.UserUpdate(disabled=True, is_active=False)
    )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "error": None,
            "data": None,
            "message": "User deleted successfully.",
        },
    )
