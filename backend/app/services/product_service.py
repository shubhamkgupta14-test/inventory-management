from datetime import datetime
from fastapi import HTTPException, status

from app.database.mongodb import db
from app.utils.helpers import serialize_mongo_document, normalize_sku, is_valid_object_id
from app.models.auth import UserRole

products_collection = db.products


# CREATE PRODUCT
async def create_product(product_data: dict, auth_user: dict):

    if auth_user["role"] == UserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )

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
async def get_all_products(auth_user: dict):
    products = []

    # superadmin can get all products, while admin and users can get active products
    if auth_user["role"] == UserRole.SUPERADMIN:
        async for product in products_collection.find():
            products.append(
                serialize_mongo_document(product)
            )
        return products

    elif auth_user["role"] == UserRole.ADMIN or auth_user["role"] == UserRole.USER:
        async for product in products_collection.find({"is_active": True}):
            products.append(
                serialize_mongo_document(product)
            )

        return products

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have permission to access this resource"
    )


# GET SINGLE PRODUCT
async def get_product_by_sku(sku: str, auth_user: dict):
    sku = normalize_sku(sku)

    if not sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid SKU"
        )

    product = await products_collection.find_one({
        "sku": sku
    })

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if auth_user["role"] == UserRole.SUPERADMIN:
        return serialize_mongo_document(product)

    elif auth_user["role"] == UserRole.ADMIN or auth_user["role"] == UserRole.USER:

        if product["is_active"]:
            return serialize_mongo_document(product)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is not active"
        )

    return serialize_mongo_document(product)


# UPDATE PRODUCT
async def update_product_by_sku(sku: str, update_data: dict, auth_user: dict):

    if auth_user["role"] == UserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )

    sku = normalize_sku(sku)

    if not sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid SKU"
        )

    update_data["updated_at"] = datetime.utcnow()

    existing_product = await products_collection.find_one({
        "sku": sku
    })

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive"
        )

    if auth_user["role"] == UserRole.SUPERADMIN:
        await products_collection.update_one(
            {"sku": sku},
            {"$set": update_data}
        )

        updated_product = await products_collection.find_one({
            "sku": sku
        })

        return serialize_mongo_document(updated_product)

    elif auth_user["role"] == UserRole.ADMIN or auth_user["role"] == UserRole.USER:
        if existing_product["is_active"]:
            await products_collection.update_one(
                {"sku": sku},
                {"$set": update_data}
            )

            updated_product = await products_collection.find_one({
                "sku": sku
            })

            return serialize_mongo_document(updated_product)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive product can not be update"
        )


# DELETE PRODUCT (soft or permanent)
async def delete_product_by_sku(sku: str,  permanent: bool, auth_user: dict):
    if auth_user["role"] == UserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )

    sku = normalize_sku(sku)

    if not sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid SKU"
        )

    existing_product = await products_collection.find_one({"sku": sku})

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if permanent:
        if auth_user["role"] == UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin can not delete the product permanently."
            )
        if existing_product["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delete product permanently only when user is inactive. Please deactivate the user first."
            )

        await products_collection.delete_one({"sku": sku})
        return {
            "success": True,
            "message": "Product permanently deleted"
        }

    else:
        if not existing_product["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product is already inactive"
            )

        await products_collection.update_one(
            {"sku": sku},
            {"$set": {
                "is_active": False,
                "updated_at": datetime.utcnow()
            }
            })

    return {
        "success": True,
        "message": "Product deactivated successfully"
    }


async def search_products_service(
    sku=None, category=None,
    supplier_id=None, is_active=None, auth_user=None
):
    filters = {}

    if auth_user["role"] != UserRole.SUPERADMIN:
        if is_active == None:
            filters["is_active"] = True

        elif not is_active:
            print(f"[DEBUG] we are here")
            return {
                "success": True,
                "count": 0,
                "data": []
            }

        filters["is_active"] = True

    else:
        if is_active is not None:
            filters["is_active"] = is_active

    if sku:
        filters["sku"] = normalize_sku(sku)

    if category:
        filters["category"] = category

    if supplier_id:
        filters["supplier_id"] = supplier_id

    products = []

    async for product in products_collection.find(filters):
        products.append(
            serialize_mongo_document(product)
        )

    return {
        "success": True,
        "count": len(products),
        "data": products
    }
