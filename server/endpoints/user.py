from datetime import datetime, timedelta
import random
import string

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from server import crud, schemas
from server.utils.auth import (
    authenticate_user,
    # create_access_token,
    get_current_user,
    get_password_hash,
    get_validate_refresh_token,
    jwt_access_token,
    jwt_refresh_token,
    refresh_to_access_token,
    verify_password,
)
from server.utils.common import validate_email_send_otp

from server.endpoints.deps import get_db


user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.post(
    "/login",
)
async def login_for_access_token(
    data: schemas.UserCreateInput, db: Session = Depends(get_db)
):
    try:
        user = authenticate_user(db, data.email, data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = jwt_access_token(data={"sub": user.email, "id": user.id})

        refresh_token = jwt_refresh_token(data={"sub": user.email, "id": user.id})
        return schemas.RespUser(
            id=user.id,
            email=user.email,
            avatar=user.avatar,
            is_verified=user.is_verified,
            providers=user.providers,
            role=user.role,
            created_at=str(user.created_at),
            updated_at=str(user.updated_at),
            token=schemas.Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            ),
        )
    except HTTPException:
        raise

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(500, "Something went wrong at server.")

    finally:
        db.close()


@user_router.post("/profile", response_model=schemas.UserProfile)
async def get_profile(current_user=Depends(get_current_user)):
    return schemas.UserProfile(
        id=current_user.id,
        email=current_user.email,
        avatar=current_user.avatar,
        role=current_user.role,
    )


@user_router.post("/signup")
async def sign_up(data: schemas.UserCreateInput, db: Session = Depends(get_db)):
    try:
        email = data.email.lower().strip()
        user = crud.user.get_by_email(db, email=email)

        if user:
            if user.is_verified:
                raise HTTPException(
                    400,
                    "You already have an account with us. please continue with login.",
                )

        else:
            hashed_password = get_password_hash(data.password)
            user = crud.user.create(
                db,
                obj_in=schemas.UserBase(
                    email=data.email, hashed_password=hashed_password
                ),
            )

        otp_sent = await validate_email_send_otp(db, email, user.id)
        if otp_sent:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "OTP sent to your email, please verify your email to continue.",
                },
            )

    except HTTPException:
        raise

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(500, "Something went wrong at server.")

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
                raise HTTPException(400, "Your email is already verified.")

        if not email_otp_obj:
            raise HTTPException(400, "First proceed via sending OTP request.")

        otp = email_otp_obj.otp
        time_now = datetime.utcnow()

        if (((time_now - email_otp_obj.updated_at).total_seconds()) / 60) < 10:
            if str(otp_sent) == str(otp):
                user_obj = crud.user.update(
                    db,
                    db_obj=user_obj,
                    obj_in=schemas.UserUpdate(is_verified=True, is_active=True),
                )
                # crud.email_otp.remove(db, id=email_otp_obj.id)
                # access_token_expires = timedelta(minutes=TOKEN_EXPIRE_DELTA)
                access_token = jwt_access_token(
                    data={"sub": user_obj.email, "id": user_obj.id}
                )

                refresh_token = jwt_refresh_token(
                    data={"sub": user_obj.email, "id": user_obj.id}
                )

                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "OTP verified successfully, thanks for signup.",
                        "data": {
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "token_type": "bearer",
                        },
                    },
                )
            else:
                raise HTTPException(400, "OTP mismatched, Please provide correct OTP.")
        else:
            crud.email_otp.remove(db, id=email_otp_obj.id)
            raise HTTPException(400, "OTP is expired, please proceed new OTP.")
    except HTTPException:
        raise

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(500, "Something went wrong at server.")

    finally:
        db.close()


@user_router.post("/resend-otp")
async def resend_otp(data: schemas.EmailSchema, db: Session = Depends(get_db)):
    try:
        email = data.email.lower().strip()
        user_obj = crud.user.get_by_email(db, email=email)
        if not user_obj:
            raise HTTPException(400, "First proceed via sending OTP request.")

        if user_obj and user_obj.is_verified:
            raise HTTPException(400, "Your email is already verified.")

        otp_sent = await validate_email_send_otp(db, email, user_obj.id)
        if otp_sent:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "OTP sent to your email, please verify your email to continue.",
                },
            )

    except HTTPException:
        raise

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(500, "Something went wrong at server.")

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
            raise HTTPException(400, "User not found.")

        if old_password == new_password:
            raise HTTPException(400, "Old password and new password are same.")

        if not verify_password(old_password, user_obj.hashed_password):
            raise HTTPException(400, "Old password is incorrect.")

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
                "message": "Password changed successfully.",
                "data": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                },
            },
        )

    except HTTPException:
        raise

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(500, "Something went wrong at server.")

    finally:
        db.close()


@user_router.post("/forgot-password-send-otp")
async def forgot_password_send_otp(
    data: schemas.EmailSchema, db: Session = Depends(get_db)
):
    try:
        email = data.email.lower().strip()
        user_obj = crud.user.get_by_email(db, email=email)
        if not user_obj:
            raise HTTPException(400, "User not found.")

        otp_sent = await validate_email_send_otp(db, email, user_obj.id)
        if otp_sent:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "OTP sent to your email, please verify your email to continue.",
                },
            )

    except HTTPException:
        raise

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(500, "Something went wrong at server.")

    finally:
        db.close()


@user_router.post("/verify-forgot-password-otp")
async def verify_forgot_password_otp(
    data: schemas.VerifyOTP, db: Session = Depends(get_db)
):
    try:
        email = data.email.lower().strip()
        otp_sent = data.otp.lower().strip()

        email_otp_obj = crud.email_otp.get_by_email(db, email=email)

        if not email_otp_obj:
            raise HTTPException(400, "OTP is not found. Please procced resend OTP.")

        otp = email_otp_obj.otp
        time_now = datetime.utcnow()

        if (((time_now - email_otp_obj.updated_at).total_seconds()) / 60) < 10:
            if str(otp_sent) == str(otp):

                crud.email_otp.remove(db, id=email_otp_obj.id)
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "OTP verified successfully, Please reset your password.",
                    },
                )
            else:
                raise HTTPException(400, "OTP not metched, Please enter valid OTP.")
        else:
            crud.email_otp.remove(db, id=email_otp_obj.id)
            raise HTTPException(400, "OTP is expired, please proceed new OTP.")

    except HTTPException:
        raise

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(500, "Something went wrong at server.")

    finally:
        db.close()


@user_router.post("/reset-forgot-password")
async def reset_forgot_password(
    data: schemas.ResetPassword, db: Session = Depends(get_db)
):
    try:
        email = data.email.lower().strip()
        new_password = data.new_password

        user = crud.user.get_by_email(db, email=email)
        if user:

            hashed_password = get_password_hash(new_password)
            user_obj = crud.user.update(
                db,
                db_obj=user,
                obj_in=schemas.UserUpdate(hashed_password=hashed_password),
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Password reset successfully, Please Login.",
                },
            )

    except HTTPException:
        raise

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(500, "Something went wrong at server.")

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

    except HTTPException:
        raise

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(500, "Something went wrong at server.")

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
                "message": "Access token generated successfully.",
                "data": {
                    "access_token": access_token,
                    "token_type": "bearer",
                },
            },
        )
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(500, "Something went wrong at server.")
