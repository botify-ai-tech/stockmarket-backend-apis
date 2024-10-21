from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import bcrypt

from server import crud, schemas
from server.config import settings
from server.endpoints.deps import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl="auth", tokenUrl="token")

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 20160


# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)


# def get_password_hash(password):
#     return pwd_context.hash(password)


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


# Function to verify the password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def authenticate_user(db, email: str, password: str):
    user = crud.user.get_by_email(db, email=email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def decode_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    return payload


def jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=2)
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return token


def jwt_access_token(data: dict):

    to_encode = data.copy()
    expire = datetime.now() + timedelta(hours=1)
    to_encode.update(
        {
            "exp": expire,
            "token_type": "access",
        }
    )

    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return access_token


def jwt_refresh_token(data: dict):

    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=7)
    to_encode.update(
        {
            "exp": expire,
            "token_type": "refresh",
        }
    )
    refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return refresh_token


def refresh_to_access_token(user):
    try:
        data = {"id": user.id, "sub": user.email}
        access = jwt_access_token(data)
        return access
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> schemas.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("id")
        if id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.user.get_by_id(db, id=id)
    if user is None:
        raise credentials_exception
    return user

def verify_pass_toekn(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> schemas.User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("id")
        if id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception
    user = crud.user.get_by_id(db, id=id)
    if user is None:
        raise credentials_exception
    return user

async def get_validate_refresh_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> schemas.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("id")
        token_type = payload["token_type"]

        if id is None or token_type != "refresh":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.user.get_by_id(db, id=id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: schemas.User = Depends(get_current_user),
) -> schemas.User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
