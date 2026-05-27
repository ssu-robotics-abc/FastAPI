from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem


def create_order(
    db: Session,
    *,
    customer_name: str,
    total_amount: int,
    payment_status: str = "paid",
) -> Order:
    order = Order(
        customer_name=customer_name,
        total_amount=total_amount,
        payment_status=payment_status,
    )
    db.add(order)
    db.flush()
    return order


def create_order_item(
    db: Session,
    *,
    order_id: int,
    product_id: int,
    quantity: int,
) -> OrderItem:
    order_item = OrderItem(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
    )
    db.add(order_item)
    return order_item
