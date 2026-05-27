from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.order import (
    PurchaseItemsRequest,
    PurchaseRequest,
    PurchaseResponse,
    PurchaseValidationResponse,
)
from app.services.order_service import (
    process_purchase_transaction,
    set_pending_purchase_items,
    validate_purchase_items,
)
from app.services.ros2_service import ros2_service


router = APIRouter()


@router.post("/purchase/validate", response_model=PurchaseValidationResponse)
def validate_purchase(
    request: PurchaseItemsRequest,
    db: Session = Depends(get_db),
) -> PurchaseValidationResponse:
    _, total_amount = validate_purchase_items(db, items=request.items)

    set_pending_purchase_items(request.items)

    return PurchaseValidationResponse(
        status="success",
        total_amount=total_amount,
        items=request.items,
        message="상품 재고 검증이 완료되었습니다.",
    )


@router.post("/purchase", response_model=PurchaseResponse)
def process_purchase(
    request: PurchaseRequest,
    db: Session = Depends(get_db),
) -> PurchaseResponse:
    order = process_purchase_transaction(
        db,
        customer_name=request.customer_name,
        items=request.items,
    )

    ros2_service.publish_purchase_complete(order.id, request.items)

    return PurchaseResponse(
        status="success",
        order_id=order.id,
        total_amount=order.total_amount,
        message=f"구매 처리가 완료되었습니다. (구매자: {request.customer_name})",
    )
