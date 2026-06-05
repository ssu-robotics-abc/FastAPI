from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.product import get_product_by_id, list_products
from app.schemas.product import ProductDisplayRead


router = APIRouter()


@router.get("/products", response_model=list[ProductDisplayRead])
def get_products(db: Session = Depends(get_db)) -> list[ProductDisplayRead]:
    return [ProductDisplayRead.from_product(product) for product in list_products(db)]


@router.get("/products/{product_id}", response_model=ProductDisplayRead)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> ProductDisplayRead:
    product = get_product_by_id(db, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="해당 상품을 찾을 수 없습니다.")

    return ProductDisplayRead.from_product(product)
