from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.crud.order import create_order, create_order_item
from app.crud.product import decrease_stock, get_product_by_name
from app.models.order import Order


def process_purchase_transaction(
    db: Session,
    *,
    customer_name: str,
    items: dict[str, int],
) -> Order:
    """구매 처리 트랜잭션입니다.

    모든 상품 존재 여부와 재고를 먼저 검증한 뒤,
    주문 생성, 주문 아이템 생성, 재고 차감을 한 번에 처리합니다.
    """

    products = {}

    for product_name, quantity in items.items():
        product = get_product_by_name(db, product_name)
        if product is None:
            raise HTTPException(
                status_code=404,
                detail=f"'{product_name}' 상품을 찾을 수 없습니다.",
            )

        if product.stock < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"'{product_name}' 재고가 부족합니다. (현재: {product.stock}개)",
            )

        products[product_name] = product

    order = create_order(db, customer_name=customer_name)

    for product_name, quantity in items.items():
        product = products[product_name]
        decrease_stock(product, quantity)
        create_order_item(
            db,
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
        )

    db.commit()
    db.refresh(order)

    return order
