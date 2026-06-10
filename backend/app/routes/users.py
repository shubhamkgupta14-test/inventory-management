from fastapi import APIRouter, Depends
from typing import Annotated

from app.services.auth_service import get_current_user

from app.models.auth import (
    CreateUserRequest,
    GetUserRequest,
    DeleteUserRequest
)

from app.services.user_service import (
    create_user,
    get_all_users,
    get_user_by_username,
    delete_user
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

user_depedency = Annotated[dict, Depends(get_current_user)]

# CREATE USER


@router.post("/create-user")
async def register_user_api(auth_user: user_depedency, user: CreateUserRequest):

    result = await create_user(user.model_dump(), auth_user=auth_user)

    return {
        "success": True,
        "message": "User registered successfully",
        "data": result
    }

# GET USER BY USERNAME


@router.post("/get-user-details")
async def get_user_api(auth_user: user_depedency, user: GetUserRequest):

    user = await get_user_by_username(user.username, auth_user)

    return {
        "success": True,
        "data": user
    }

# GET ALL USERS


@router.get("/")
async def get_users_api(auth_user: user_depedency):

    users = await get_all_users(auth_user)

    return {
        "success": True,
        "count": len(users),
        "data": users
    }

# DELETE USER


@router.delete("/delete-user")
async def delete_user_api(auth_user: user_depedency, user: DeleteUserRequest):

    result = await delete_user(username=user.username, permanent=user.permanent, auth_user=auth_user)

    return {
        "success": True,
        "message": "User deleted successfully",
        "data": result
    }
