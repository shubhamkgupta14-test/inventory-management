from datetime import datetime
from fastapi import HTTPException, status

from app.database.mongodb import db
from app.utils.helpers import serialize_mongo_document, normalize_sku


products_collection = db.products


# CREATE PRODUCT
async def create_product(product_data: dict):

    # Check duplicate SKU
    existing_product = await products_collection.find_one({
        "sku": product_data["sku"]
    })

    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product with this SKU already exists"
        )

    product_data["created_at"] = datetime.utcnow()
    product_data["updated_at"] = datetime.utcnow()

    result = await products_collection.insert_one(product_data)

    created_product = await products_collection.find_one({
        "_id": result.inserted_id
    })

    return serialize_mongo_document(created_product)


# GET ALL PRODUCTS
async def get_all_products():

    products = []

    async for product in products_collection.find({"is_active": True}):
        products.append(
            serialize_mongo_document(product)
        )

    return products


# GET SINGLE PRODUCT
async def get_product_by_sku(sku: str):
    sku = normalize_sku(sku)

    if not sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid SKU"
        )

    product = await products_collection.find_one({
        "sku": sku,
        "is_active": True
    })

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return serialize_mongo_document(product)


# UPDATE PRODUCT
async def update_product_by_sku(sku: str, update_data: dict):
    sku = normalize_sku(sku)

    if not sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid SKU"
        )

    update_data["updated_at"] = datetime.utcnow()

    existing_product = await products_collection.find_one({
        "sku": sku,
        "is_active": True
    })

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive"
        )

    await products_collection.update_one(
        {"sku": sku},
        {"$set": update_data}
    )

    updated_product = await products_collection.find_one({
        "sku": sku
    })

    return serialize_mongo_document(updated_product)


# DELETE PRODUCT (soft or permanent)
async def delete_product_by_sku(sku: str, permanent: bool = False):
    sku = normalize_sku(sku)

    if not sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid SKU"
        )

    if permanent:
        # Permanently delete from database
        existing_product = await products_collection.find_one({"sku": sku})

        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        await products_collection.delete_one({"sku": sku})
    else:
        # Soft delete - mark as inactive
        existing_product = await products_collection.find_one({
            "sku": sku,
            "is_active": True
        })

        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or inactive"
            )

        await products_collection.update_one(
            {"sku": sku},
            {"$set": {"is_active": False}}
        )

    return True
