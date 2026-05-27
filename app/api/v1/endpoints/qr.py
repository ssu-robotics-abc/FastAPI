from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.order import QRPaymentRequest, PurchaseResponse
from app.services.order_service import (
    clear_pending_purchase_items,
    get_pending_purchase_items,
    process_purchase_transaction,
)
from app.services.ros2_service import ros2_service


router = APIRouter()


@router.post("/qr_scan_complete", response_model=PurchaseResponse)
def process_qr_scan_complete(
    request: QRPaymentRequest,
    db: Session = Depends(get_db),
) -> PurchaseResponse:
    items = get_pending_purchase_items()

    order = process_purchase_transaction(
        db,
        customer_name=request.customer_name,
        items=items,
    )
    clear_pending_purchase_items()

    ros2_service.publish_qr_scan_complete(request.customer_name)
    ros2_service.publish_purchase_complete(order.id, items)

    return PurchaseResponse(
        status="success",
        order_id=order.id,
        total_amount=order.total_amount,
        message=f"QR 결제 및 구매 처리가 완료되었습니다. (구매자: {request.customer_name})",
    )
