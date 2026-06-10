from jose import jwt, JWTError
from typing import Annotated
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.database.mongodb import db

SECRET_KEY = 'QZ7PYvWcTMLnKINQPWoBT6L3oEwPF-0zG-H0VltRaBUr5Pj7TSkR6w=='
ALGORITHM = 'HS256'

TOKEN_URL = '/auth/token'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)
user_collection = db.users


async def authenticate_user(username: str, password: str, user_collection):
    user = await user_collection.find_one({"username": username})

    if not user:
        return False

    if not bcrypt_context.verify(password, user["password"]):
        return False

    return user


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication token or token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        role: str = payload.get("role")

        if user_id is None or username is None or role is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = user_collection.find_one({"_id": user_id})

    if user is None:
        raise credentials_exception

    return {
        "user_id": user_id,
        "username": username,
        "role": role
    }


async def create_access_token(user_id: str, username: str, role: str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    to_encode = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": expire
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_token_service(username: str, password: str):
    user = await user_collection.find_one({"username": username})
    if not user:
        raise HTTPException(
            status_code=401, detail="Invalid username or password")

    if user.get("active") is False:
        raise HTTPException(
            status_code=403, detail="User account is inactive")

    if not bcrypt_context.verify(password, user["password"]):
        raise HTTPException(
            status_code=401, detail="Invalid username or password")

    token = await create_access_token(user["_id"], user["username"], user["role"])

    return {"access_token": token, "token_type": "bearer"}
