from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.product import get_product_by_barcode
from app.schemas.scan import ScanRequest, ScanResponse
from app.services.ros2_service import ros2_service


router = APIRouter()


@router.post("/scan", response_model=ScanResponse)
def process_barcode_scan(
    request: ScanRequest,
    db: Session = Depends(get_db),
) -> ScanResponse:
    product = get_product_by_barcode(db, request.barcode_data)

    if product is None:
        raise HTTPException(status_code=404, detail="등록되지 않은 바코드입니다.")

    ros2_service.publish_scan_event(product.name)

    return ScanResponse(
        product_name=product.name,
        message="스캔 완료 신호가 전송되었습니다.",
    )
