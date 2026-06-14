from datetime import datetime, UTC

from app.database.mongodb import db
from app.models.stock import StockStatus

from app.utils.settings import Settings

from app.utils.helpers import (
    round_price,
    round_final_amount,
    normalize_sku
)
from app.utils.responseBuilder import build_stock_response

from app.utils.messages import Messages
from app.models.auth import UserRole

from app.core.exceptions import (
    forbidden,
    not_found,
    bad_request
)
stocks_collection = db.stocks


def calculate_stock_status(quantity: int):

    if quantity <= Settings.OUT_OF_STOCK_CHECK:
        return StockStatus.OUT_OF_STOCK

    if quantity < Settings.LOW_STOCK_CHECK:
        return StockStatus.LOW_QUANTITY

    return StockStatus.IN_STOCK


async def increase_stock(
    sku: str,
    name: str,
    quantity: int,
    unit_price: float
):

    existing_stock = await stocks_collection.find_one({
        "sku": sku
    })

    # CREATE NEW STOCK
    if not existing_stock:

        avg_price = round_price(unit_price)

        inventory_value = round_final_amount(
            quantity * avg_price,
        )

        stock_data = {
            "sku": sku,
            "name": name,
            "quantity": quantity,
            "avg_price": avg_price,
            "inventory_value": inventory_value,
            "stock_status": calculate_stock_status(
                quantity
            ),
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC)
        }

        await stocks_collection.insert_one(
            stock_data
        )
        return

    # UPDATE EXISTING STOCK
    old_quantity = existing_stock.get(
        "quantity",
        0
    )

    old_avg_price = existing_stock.get(
        "avg_price",
        0
    )

    new_quantity = old_quantity + quantity

    total_old_value = old_quantity * old_avg_price

    total_new_value = quantity * unit_price

    avg_price = round_price(
        (total_old_value + total_new_value) / new_quantity
    )

    inventory_value = round_final_amount(
        new_quantity * avg_price
    )

    await stocks_collection.update_one(
        {
            "sku": sku
        },
        {
            "$set": {
                "quantity": new_quantity,
                "avg_price": avg_price,
                "inventory_value": inventory_value,
                "stock_status": calculate_stock_status(
                    new_quantity
                ),
                "updated_at": datetime.now(UTC)
            }
        }
    )


async def decrease_stock(
    sku: str,
    quantity: int
):

    existing_stock = await stocks_collection.find_one({
        "sku": sku
    })

    if not existing_stock:
        return False

    current_quantity = existing_stock.get(
        "quantity",
        0
    )

    if current_quantity < quantity:
        return False

    new_quantity = current_quantity - quantity

    avg_price = existing_stock.get(
        "avg_price",
        0
    )

    inventory_value = round_final_amount(
        new_quantity * avg_price
    )

    await stocks_collection.update_one(
        {
            "sku": sku
        },
        {
            "$set": {
                "quantity": new_quantity,
                "inventory_value": inventory_value,
                "stock_status": calculate_stock_status(
                    new_quantity
                ),
                "updated_at": datetime.now(UTC)
            }
        }
    )

    return True


async def get_stocks(
    auth_user: dict,
    sku: str = None,
    stock_status: str = None,
    sort_by: str = "created_at",
    sort_order: int = "desc"
):

    if auth_user.get("role") not in [
        UserRole.SUPERADMIN,
        UserRole.ADMIN,
        UserRole.USER
    ]:
        forbidden()

    filters = {}

    if sku:
        filters["sku"] = normalize_sku(sku)

    if stock_status:
        valid_status = [status.value for status in StockStatus]

        if stock_status not in valid_status:
            bad_request(Messages.INVALID_STOCK_STATUS)

        filters["stock_status"] = stock_status

    stocks = []

    sort_order = -1 if sort_order.lower() == "desc" else 1

    async for stock in stocks_collection.find(
        filters
    ).sort(sort_by, sort_order):

        stocks.append(
            build_stock_response(stock)
        )

    return stocks
