from fastapi import FastAPI

from app.routes.products import router as product_router

app = FastAPI(
    title="Inventory Management API",
)

app.include_router(product_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Inventory Management API!"}
