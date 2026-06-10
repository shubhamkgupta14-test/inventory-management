from app.database.mongodb import db
import os
from datetime import datetime
from app.models.auth import UserRole
from app.utils.helpers import hash_password

users_collection = db.users


async def create_default_superadmin():
    existing_superadmin = await users_collection.find_one({
        "role": UserRole.SUPERADMIN
    })

    if not existing_superadmin:
        superadmin_data = {
            "username": os.getenv(
                "SUPERADMIN_USERNAME"
            ),
            "password": hash_password(os.getenv("SUPERADMIN_PASSWORD")),
            "role": UserRole.SUPERADMIN,
            "active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        await users_collection.insert_one(
            superadmin_data
        )
    return True
