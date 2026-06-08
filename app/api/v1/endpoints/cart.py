from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas.cart import CartQueueAcceptedResponse, CartQueueItem, CartQueueResponse
from app.services.cart_queue import (
    connect_cart_queue_websocket,
    disconnect_cart_queue_websocket,
    enqueue_cart_job,
    list_cart_jobs,
    send_cart_queue_snapshot,
)


router = APIRouter()


@router.get("/cart", response_model=CartQueueResponse)
async def list_cart_queue() -> CartQueueResponse:
    return CartQueueResponse(jobs=await list_cart_jobs())


@router.post("/cart", response_model=CartQueueAcceptedResponse)
async def receive_orders(orders: list[CartQueueItem]) -> CartQueueAcceptedResponse:
    job = await enqueue_cart_job(orders)

    print(f"\n📦 [서버] 새로운 작업 큐 접수! job_id={job.job_id} / 총 {len(orders)}종류의 상품")
    for item in orders:
        print(f" └─ 상품 ID: {item.id} | 수량: {item.amount}개")

    return CartQueueAcceptedResponse(
        status="success",
        message=f"{len(orders)}개의 주문 작업이 큐에 정상 접수되었습니다.",
        job=job,
    )


@router.websocket("/cart/ws")
async def stream_cart_queue(websocket: WebSocket) -> None:
    await connect_cart_queue_websocket(websocket)
    try:
        await send_cart_queue_snapshot(websocket)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await disconnect_cart_queue_websocket(websocket)
