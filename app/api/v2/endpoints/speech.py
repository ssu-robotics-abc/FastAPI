from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ros2_service import ros2_service


router = APIRouter()


class StartSttResponse(BaseModel):
    status: str
    message: str


@router.post("/speech/start-stt", response_model=StartSttResponse)
def start_stt() -> StartSttResponse:
    if not ros2_service.start_stt():
        raise HTTPException(
            status_code=503,
            detail="STT 시작 서비스를 호출할 수 없습니다.",
        )

    return StartSttResponse(
        status="success",
        message="STT 시작 명령을 전송했습니다.",
    )
