from fastapi import APIRouter, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.models.auth import Token

from app.services.auth_service import (
    get_token_service
)


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/token", response_model=Token)
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return await get_token_service(form_data.username, form_data.password)
