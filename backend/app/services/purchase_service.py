from datetime import datetime, UTC
from bson import ObjectId
from app.database.mongodb import db

from app.models.auth import UserRole
from app.models.purchase import PaymentStatus, PurchaseStatus

from app.core.exceptions import (
    forbidden,
    not_found,
    bad_request
)

from app.utils.messages import Messages
from app.utils.helpers import (
    is_valid_object_id,
    build_purchase_response,
    normalize_sku,
    round_price,
    round_final_amount
)
purchase_collection = db.purchases
products_collection = db.products
# suppliers_collection = db.suppliers
# stocks_collection = db.stocks


async def create_purchase(
    auth_user: dict,
    purchase_data: dict
):

    if auth_user.get("role") == UserRole.USER:
        forbidden()

    subtotal = 0
    total_tax = 0
    total_discount = 0

    purchase_items = []
    print(f"[DEBUG] {purchase_data}")

    for item in purchase_data.get("items"):

        sku = normalize_sku(item.get("sku"))

        product = await products_collection.find_one({
            "sku": sku
        })

        if not product:
            not_found(Messages.PRODUCT_NOT_FOUND)

        if (
            auth_user.get("role") == UserRole.ADMIN
            and not product.get("is_active")
        ):
            forbidden(Messages.PRODUCT_INACTIVE)

        supplier_id = product.get("supplier_id")

        quantity = item.get("quantity")
        unit_price = item.get("unit_price")

        tax_percentage = product.get("tax_rate", 0)

        discount_percentage = item.get(
            "discount_percentage",
            0
        )

        item_subtotal = round_price(
            quantity * unit_price
        )

        tax_amount = round_price(
            (item_subtotal * tax_percentage) / 100
        )

        discount_amount = round_price(
            (item_subtotal * discount_percentage) / 100
        )

        total_price = round_price(
            item_subtotal +
            tax_amount -
            discount_amount
        )

        subtotal += round_price(item_subtotal)
        total_tax += round_price(tax_amount)
        total_discount += round_price(discount_amount)

        purchase_items.append({
            "sku": sku,
            "name": product.get("name"),
            "quantity": quantity,
            "unit_price": unit_price,
            "subtotal": item_subtotal,
            "tax_percentage": tax_percentage,
            "tax_amount": tax_amount,
            "discount_percentage": discount_percentage,
            "discount_amount": discount_amount,
            "total_price": total_price
        })

    final_total_amount = round_final_amount(
        subtotal +
        total_tax -
        total_discount
    )

    total_paid = sum(
        payment.get("amount_paid", 0)
        for payment in purchase_data.get(
            "payment_details",
            []
        )
    )

    remaining_amount = (
        final_total_amount - total_paid
    )

    if remaining_amount <= 0:
        payment_status = PaymentStatus.PAID

    elif total_paid > 0:
        payment_status = PaymentStatus.PARTIAL

    else:
        payment_status = PaymentStatus.UNPAID

    # invoice_id = await generate_invoice_id()

    purchase_document = {
        "invoice_id": purchase_data.get("invoice_id"),
        "supplier_id": supplier_id,
        "items": purchase_items,
        "subtotal": subtotal,
        "total_tax": total_tax,
        "total_discount": total_discount,
        "final_total_amount": final_total_amount,
        "total_paid": total_paid,
        "remaining_amount": remaining_amount,
        "payment_status": payment_status,
        "payment_details": purchase_data.get(
            "payment_details",
            []
        ),
        "purchase_status": PurchaseStatus.COMPLETED,
        "notes": purchase_data.get("notes"),
        "created_by": auth_user.get(
            "username"
        ),
        "stock_updated": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }

    result = await purchase_collection.insert_one(
        purchase_document
    )

    created_purchase = await purchase_collection.find_one({
        "_id": result.inserted_id
    })

    return build_purchase_response(
        created_purchase
    )


async def get_purchases(
    auth_user: dict,
    purchase_id: str = None,
    invoice_id: str = None,
    supplier_id: str = None,
    sort_by: str = "created_at",
    order: str = "desc"
):
    if auth_user.get("role") not in [
        UserRole.SUPERADMIN,
        UserRole.ADMIN,
        UserRole.USER
    ]:
        forbidden()

    filters = {}
    purchases = []
    allowed_sort_fields = [
        "created_at",
        "updated_at",
        "invoice_id",
        "supplier_id"
    ]

    if purchase_id:
        if not is_valid_object_id(purchase_id):
            bad_request(Messages.INVALID_PURCHASE_ID)

        filters["_id"] = ObjectId(purchase_id)

    if invoice_id:
        filters["invoice_id"] = invoice_id

    if supplier_id:
        filters["supplier_id"] = supplier_id

    if sort_by not in allowed_sort_fields:
        bad_request(Messages.INVALID_SORT_FIELD)

    sort_order = -1 if order.lower() == "desc" else 1

    async for purchase in purchase_collection.find(filters).sort(sort_by, sort_order):

        purchases.append(
            build_purchase_response(purchase)
        )

    return purchases


async def get_purchase_by_purchase_id(
    auth_user: dict,
    purchase_id: str
):
    if auth_user.get("role") not in [
        UserRole.SUPERADMIN,
        UserRole.ADMIN,
        UserRole.USER
    ]:
        forbidden()

    if not is_valid_object_id(purchase_id):
        bad_request(Messages.INVALID_PURCHASE_ID)

    purchase = await purchase_collection.find_one({
        "_id": ObjectId(purchase_id)
    })

    if not purchase:
        not_found(Messages.PURCHASE_NOT_FOUND)

    return build_purchase_response(purchase)
