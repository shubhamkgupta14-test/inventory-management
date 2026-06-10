from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes.products import router as product_router
from app.routes.users import router as user_router
from app.routes.auth_route import router as auth_router
from app.seeds.superadmin_seed import create_default_superadmin

# STARTUP EVENT


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create_default_superadmin()
    print("Starting up the Inventory Management API...")
    await create_default_superadmin();
    yield
    print("Shutting down the Inventory Management API...")


app = FastAPI(
    title="Inventory Management API",
    lifespan=lifespan
)


# ROUTERS
app.include_router(product_router)
app.include_router(user_router)
app.include_router(auth_router)

# ROOT


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Inventory Management API!",
        "documentation": "Use /docs for API documentation."
    }

# HEALTH CHECK


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "API is healthy and running."
    }
