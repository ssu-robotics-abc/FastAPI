from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.product import get_product_by_name
from app.schemas.product import StockResponse


router = APIRouter()


@router.get("/stock/{product_name}", response_model=StockResponse)
def get_product_stock(
    product_name: str,
    db: Session = Depends(get_db),
) -> StockResponse:
    product = get_product_by_name(db, product_name)

    if product is None:
        raise HTTPException(status_code=404, detail="해당 상품을 찾을 수 없습니다.")

    return StockResponse(
        product_name=product.name,
        remaining_stock=product.stock,
        barcode_data=product.barcode_data,
    )
