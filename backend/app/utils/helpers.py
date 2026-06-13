from bson import ObjectId
from passlib.context import CryptContext
from math import ceil


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


def round_price(value: float):
    return round(value, 2)


def round_final_amount(value: float):
    return float(ceil(value))


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


def build_purchase_response(purchase: dict):
    return {
        "purchase_id": str(purchase["_id"]),
        "invoice_id": purchase.get(
            "invoice_id"
        ),
        "supplier_id": purchase.get(
            "supplier_id"
        ),
        "items": purchase.get("items"),
        "subtotal": purchase.get(
            "subtotal"
        ),
        "total_tax": purchase.get(
            "total_tax"
        ),
        "total_discount": purchase.get(
            "total_discount"
        ),
        "final_total_amount": purchase.get(
            "final_total_amount"
        ),
        "total_paid": purchase.get(
            "total_paid"
        ),
        "remaining_amount": purchase.get(
            "remaining_amount"
        ),
        "payment_status": purchase.get(
            "payment_status"
        ),
        "payment_details": purchase.get(
            "payment_details"
        ),
        "purchase_status": purchase.get(
            "purchase_status"
        ),
        "notes": purchase.get("notes"),
        "created_by": purchase.get(
            "created_by"
        ),
        "created_at": purchase.get(
            "created_at"
        ).isoformat(),
        "updated_at": purchase.get(
            "updated_at"
        ).isoformat(),
    }


def build_sales_response(sale: dict):
    return {
        "sale_id": str(sale.get("_id", "")),
        "invoice_id": sale.get("invoice_id"),
        "user_info": sale.get("user_info"),
        "items": sale.get("items", []),

        "subtotal": sale.get("subtotal", 0),
        "total_tax": sale.get("total_tax", 0),
        "total_discount": sale.get("total_discount", 0),
        "final_total_amount": sale.get("final_total_amount", 0),

        "payment_details": sale.get("payment_details", []),

        "sale_status": sale.get("sale_status", "SOLD"),

        "notes": sale.get("notes"),

        "created_at": sale.get("created_at").isoformat(),
        "updated_at": sale.get("updated_at").isoformat()
    }
