from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.crud.order import create_order, create_order_item
from app.crud.product import decrease_stock, get_product_by_name
from app.models.order import Order
from app.models.product import Product


_pending_purchase_items: dict[str, int] | None = None


def set_pending_purchase_items(items: dict[str, int]) -> None:
    global _pending_purchase_items
    _pending_purchase_items = dict(items)


def get_pending_purchase_items() -> dict[str, int]:
    if _pending_purchase_items is None:
        raise HTTPException(
            status_code=400,
            detail="결제 대기 중인 구매 예정 품목이 없습니다.",
        )
    return dict(_pending_purchase_items)


def clear_pending_purchase_items() -> None:
    global _pending_purchase_items
    _pending_purchase_items = None


def validate_purchase_items(
    db: Session,
    *,
    items: dict[str, int],
) -> tuple[dict[str, Product], int]:
    """상품 존재 여부와 재고를 검증하고 구매 예정 총액을 계산합니다."""

    products = {}
    total_amount = 0

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
        total_amount += product.price * quantity

    return products, total_amount


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

    products, total_amount = validate_purchase_items(db, items=items)

    order = create_order(
        db,
        customer_name=customer_name,
        total_amount=total_amount,
    )

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
