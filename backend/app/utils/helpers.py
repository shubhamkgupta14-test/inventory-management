from bson import ObjectId
from passlib.context import CryptContext


def serialize_mongo_document(document):
    if not document:
        return None
    document["id"] = str(document["_id"])
    del document["_id"]
    return document


def is_valid_object_id(id: str):
    return ObjectId.is_valid(id)


def normalize_sku(sku: str):
    if not isinstance(sku, str):
        return ""
    sku = sku.strip().upper()
    return "-".join(sku.split())


def hash_password(password: str):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)
