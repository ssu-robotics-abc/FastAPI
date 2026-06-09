from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.crud.order import create_order, create_order_item
from app.crud.product import get_product_by_name
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

    모든 상품 존재 여부와 현재 재고를 확인한 뒤, 재고 차감은 조건부
    UPDATE로 처리합니다. 여러 키오스크가 동시에 주문해도 stock >= quantity
    조건을 통과한 요청만 차감되며, 실패하면 주문 전체를 롤백합니다.
    """

    products, total_amount = validate_purchase_items(db, items=items)

    try:
        order = create_order(
            db,
            customer_name=customer_name,
            total_amount=total_amount,
        )

        for product_name, quantity in items.items():
            product = products[product_name]
            result = db.execute(
                update(Product)
                .where(Product.id == product.id, Product.stock >= quantity)
                .values(stock=Product.stock - quantity)
            )
            if result.rowcount != 1:
                db.rollback()
                current_product = get_product_by_name(db, product_name)
                current_stock = current_product.stock if current_product else 0
                raise HTTPException(
                    status_code=400,
                    detail=f"'{product_name}' 재고가 부족합니다. (현재: {current_stock}개)",
                )

            create_order_item(
                db,
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
            )

        db.commit()
        db.refresh(order)
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise

    return order
