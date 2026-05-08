from fastapi import APIRouter

from app.api.v1.endpoints import purchase, qr, scan, stock


api_router = APIRouter()
api_router.include_router(stock.router, tags=["stock"])
api_router.include_router(scan.router, tags=["scan"])
api_router.include_router(purchase.router, tags=["purchase"])
api_router.include_router(qr.router, tags=["qr"])
