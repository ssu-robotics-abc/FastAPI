from fastapi import APIRouter

from app.api.v2.endpoints import products, speech


api_router = APIRouter()
api_router.include_router(products.router, tags=["products"])
api_router.include_router(speech.router, tags=["speech"])
