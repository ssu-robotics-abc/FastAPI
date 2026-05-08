from fastapi import APIRouter

from app.schemas.scan import QRScanRequest, QRScanResponse
from app.services.ros2_service import ros2_service


router = APIRouter()


@router.post("/qr_scan_complete", response_model=QRScanResponse)
def process_qr_scan_complete(request: QRScanRequest) -> QRScanResponse:
    ros2_service.publish_qr_scan_complete(request.customer_name)

    return QRScanResponse(
        status="success",
        message=f"[{request.customer_name}]님의 QR 스캔 완료 신호가 ROS 2로 전송되었습니다.",
    )
