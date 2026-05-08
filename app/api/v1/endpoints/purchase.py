from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.order import PurchaseRequest, PurchaseResponse
from app.services.order_service import process_purchase_transaction
from app.services.ros2_service import ros2_service


router = APIRouter()


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
        message=f"구매 처리가 완료되었습니다. (구매자: {request.customer_name})",
    )
