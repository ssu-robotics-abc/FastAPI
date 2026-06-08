from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
from typing import List

from app.api.deps import get_db
from app.crud.product import get_product_by_id, list_products
from app.schemas.product import ProductRead


router = APIRouter()
class OrderItem(BaseModel):
    id: str
    amount: int


@router.post("/cart")
async def receive_orders(orders: List[OrderItem]):
    
    print(f"\n📦 [서버] 새로운 주문 접수! 총 {len(orders)}종류의 상품")
    
    for item in orders:
        print(f" └─ 상품 ID: {item.id} | 수량: {item.amount}개")

    # TODO: 주문 처리 로직 추가

    return {"status": "success", "message": f"{len(orders)}개의 주문 정상 접수"}
