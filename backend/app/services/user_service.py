from datetime import datetime
from fastapi import HTTPException, status

from app.database.mongodb import db
from app.utils.helpers import serialize_mongo_document, hash_password

from app.models.auth import UserRole


user_collection = db.users

# CREATE USER


async def create_user(user_data: dict, auth_user: dict = None):

    if auth_user["role"] != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )

    # Check duplicate username
    existing_user = await user_collection.find_one({
        "username": user_data["username"]
    })

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username already exists"
        )

    user_data["created_at"] = datetime.utcnow()
    user_data["updated_at"] = datetime.utcnow()
    user_data["active"] = True
    user_data["role"] = UserRole.USER
    user_data["password"] = hash_password(user_data["password"])

    result = await user_collection.insert_one(user_data)

    created_user = await user_collection.find_one({
        "_id": result.inserted_id
    })

    return serialize_mongo_document(created_user)


# GET USER BY USERNAME
async def get_user_by_username(username: str, auth_user: dict):

    user = await user_collection.find_one({
        "username": username
    })

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # superadmin can view all users including inactive users, superadmin and admin users
    if auth_user["role"] == UserRole.SUPERADMIN:
        return serialize_mongo_document(user)

    # admin can view only active users and cannot view other admin and superadmin users
    elif auth_user["role"] == UserRole.ADMIN:
        if user["username"] == auth_user["username"]:
            return serialize_mongo_document(user)

        if user["role"] != UserRole.USER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource"
            )

        if not user["active"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or inactive"
            )

        return serialize_mongo_document(user)

    # users can view only their details
    elif auth_user["role"] == UserRole.USER:
        if auth_user["username"] != username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource"
            )
        return serialize_mongo_document(user)

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid role")

# GET ALL USERS


async def get_all_users(auth_user: dict):

    users = []
    # superadmin can view all users including inactive users, superadmin and admin users
    # admin can view only active users and cannot view other admin and superadmin users, also can view own details
    # users cannot view all users.

    if auth_user["role"] == UserRole.SUPERADMIN:
        async for user in user_collection.find({}):
            users.append(
                serialize_mongo_document(user)
            )

        return users

    elif auth_user["role"] == UserRole.ADMIN:
        async for user in user_collection.find({
            "$or": [
                {
                    "username": auth_user["username"]
                },
                {
                    "active": True,
                    "role": UserRole.USER
                }
            ]
        }):
            users.append(
                serialize_mongo_document(user)
            )

        return users

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have permission to access this resource")

# DELETE USER SOFT AND PERMANENT


async def delete_user(username: str, permanent: bool = False, auth_user: dict = None):
    # only superadmin can delete users, no other role can delete

    if auth_user["role"] != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )

    existing_user = await user_collection.find_one({
        "username": username,
    })

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # PREVENT SELF DELETE
    if auth_user["username"] == username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account"
        )

    # PREVENT SUPERADMIN DELETE
    if existing_user.get("role") == UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete superadmin user"
        )

    if permanent:
        if existing_user.get("active"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delete user permanently only when user is inactive. Please deactivate the user first."
            )

        await user_collection.delete_one({
            "username": username
        })

        return {
            "success": True,
            "message": "User permanently deleted"
        }

    else:
        if not existing_user.get("active"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already inactive"
            )

        await user_collection.update_one({
            "username": username
        }, {
            "$set": {
                "active": False,
                "updated_at": datetime.utcnow()
            }
        })
    return {
        "success": True,
        "message": "User deactivated successfully"
    }
