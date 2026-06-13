from bson import ObjectId
from passlib.context import CryptContext


def serialize_mongo_document(document):
    if not document:
        return None
    document["id"] = str(document["_id"])
    del document["_id"]
    document.pop("password", None)
    return document


def is_valid_object_id(id: str):
    return ObjectId.is_valid(id)


def normalize_sku(sku: str):
    if not isinstance(sku, str):
        return ""
    sku = sku.strip().upper()
    return "-".join(sku.split())


def normalize_username(username: str):
    return username.strip().lower()


def hash_password(password: str):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def build_user_response(user: dict):
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "role": user["role"],
        "active": user["active"],
        "created_at": user["created_at"].isoformat(),
        "updated_at": user["updated_at"].isoformat()
    }


def build_product_response(product: dict):
    return {
        "id": str(product["_id"]),
        "sku": product["sku"],
        "name": product["name"],
        "description": product["description"],
        "category": product["category"],
        "unit_of_measure": product["unit_of_measure"],
        "tax_rate": product["tax_rate"],
        "reorder_level": product["reorder_level"],
        "attributes": {
            "color": product["attributes"].get("color"),
            "material": product["attributes"].get('material'),
            "weight": product["attributes"].get("weight"),
            "size": product["attributes"].get("size"),
            "dimension": product["attributes"].get("dimension")
        },
        "supplier_id": product["supplier_id"],
        "is_active": product["is_active"],
        "created_at": product["created_at"].isoformat(),
        "updated_at": product["updated_at"].isoformat()
    }
