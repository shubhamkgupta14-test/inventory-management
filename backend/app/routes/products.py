from fastapi import APIRouter, HTTPException, status, Query

from app.models.product import (
    ProductCreate,
    ProductUpdate
)

from app.services.product_service import (
    create_product,
    get_all_products,
    get_product_by_sku,
    update_product_by_sku,
    delete_product_by_sku
)

from app.utils.helpers import normalize_sku


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# CREATE PRODUCT
@router.post("/")
async def create_product_api(product: ProductCreate):

    result = await create_product(
        product.model_dump()
    )

    return {
        "success": True,
        "message": "Product created successfully",
        "data": result
    }


# GET ALL PRODUCTS
@router.get("/")
async def get_products_api():

    products = await get_all_products()

    return {
        "success": True,
        "count": len(products),
        "data": products
    }


# GET PRODUCT BY SKU
@router.get("/{sku}")
async def get_product_api(sku: str):
    sku = normalize_sku(sku)

    if not sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid SKU"
        )

    product = await get_product_by_sku(sku)

    return {
        "success": True,
        "data": product
    }


# UPDATE PRODUCT
@router.put("/{sku}")
async def update_product_api(
    sku: str,
    product: ProductUpdate
):
    sku = normalize_sku(sku)

    if not sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid SKU"
        )

    update_data = product.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    updated_product = await update_product_by_sku(
        sku,
        update_data
    )

    return {
        "success": True,
        "message": "Product updated successfully",
        "data": updated_product
    }


# DELETE PRODUCT (soft or permanent)
@router.delete("/{sku}")
async def delete_product_api(
    sku: str,
    permanent: bool = Query(
        False, description="Permanently delete (true) or soft delete (false)")
):
    sku = normalize_sku(sku)

    if not sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid SKU"
        )

    await delete_product_by_sku(sku, permanent=permanent)

    message = "Product permanently deleted successfully" if permanent else "Product deleted successfully"
    return {
        "success": True,
        "message": message
    }
