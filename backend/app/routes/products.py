from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Annotated, Optional

from app.services.auth_service import get_current_user

from app.models.product import (
    ProductCreate,
    ProductUpdate,
    ProductDeleteRequest
)

from app.services.product_service import (
    create_product,
    get_all_products,
    get_product_by_sku,
    update_product_by_sku,
    delete_product_by_sku,
    search_products_service
)

from app.utils.helpers import normalize_sku


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

user_depedency = Annotated[dict, Depends(get_current_user)]


# CREATE PRODUCT
@router.post("/create-product")
async def create_product_api(auth_user: user_depedency, product: ProductCreate):

    result = await create_product(
        product.model_dump(),
        auth_user
    )

    return {
        "success": True,
        "message": "Product created successfully",
        "data": result
    }


# GET ALL PRODUCTS
@router.get("/")
async def get_products_api(auth_user: user_depedency):

    products = await get_all_products(auth_user)

    return {
        "success": True,
        "count": len(products),
        "data": products
    }


# GET PRODUCT BY SKU
@router.get("/get-product-details/{sku}")
async def get_product_api(auth_user: user_depedency, sku: str):
    sku = normalize_sku(sku)

    if not sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid SKU"
        )

    product = await get_product_by_sku(sku, auth_user)

    return {
        "success": True,
        "data": product
    }


# UPDATE PRODUCT
@router.put("/update-product/{sku}")
async def update_product_api(
    auth_user: user_depedency,
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
        update_data,
        auth_user
    )

    return {
        "success": True,
        "message": "Product updated successfully",
        "data": updated_product
    }


# DELETE PRODUCT (soft or permanent)
@router.delete("/delete-product")
async def delete_product_api(
        auth_user: user_depedency,
        product: ProductDeleteRequest):
    sku = normalize_sku(product.sku)

    if not sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid SKU"
        )

    await delete_product_by_sku(product.sku, product.permanent, auth_user)

    message = "Product permanently deleted successfully" if product.permanent else "Product deleted successfully"
    return {
        "success": True,
        "message": message
    }

# SEARCH PRODUCTS


@router.get("/search")
async def search_products(
    auth_user: user_depedency,
    sku: Optional[str] = None,
    category: Optional[str] = None,
    supplier_id: Optional[str] = None,
    is_active: Optional[bool] = True
):
    return await search_products_service(
        sku=sku, category=category,
        supplier_id=supplier_id, is_active=is_active, auth_user=auth_user
    )
