import asyncio
from collections import deque
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import WebSocket

from app.schemas.cart import CartQueueItem, CartQueueJob

MAX_CART_QUEUE_LENGTH = 100

_cart_jobs: deque[CartQueueJob] = deque(maxlen=MAX_CART_QUEUE_LENGTH)
_queue_lock = asyncio.Lock()
_connection_lock = asyncio.Lock()
_active_websockets: set[WebSocket] = set()


def _serialize_job(job: CartQueueJob) -> dict:
    return job.model_dump(mode="json")


def _serialize_jobs(jobs: list[CartQueueJob]) -> list[dict]:
    return [_serialize_job(job) for job in jobs]


async def list_cart_jobs() -> list[CartQueueJob]:
    async with _queue_lock:
        return list(_cart_jobs)


async def enqueue_cart_job(items: list[CartQueueItem]) -> CartQueueJob:
    job = CartQueueJob(
        job_id=f"cart-{uuid4().hex[:12]}",
        created_at=datetime.now(timezone.utc),
        items=[CartQueueItem.model_validate(item) for item in items],
        total_item_count=sum(item.amount for item in items),
    )

    async with _queue_lock:
        _cart_jobs.append(job)
        jobs_snapshot = list(_cart_jobs)

    await broadcast_cart_queue_event(
        {
            "type": "cart_job_created",
            "job": _serialize_job(job),
            "jobs": _serialize_jobs(jobs_snapshot),
        }
    )
    return job


async def connect_cart_queue_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    async with _connection_lock:
        _active_websockets.add(websocket)


async def disconnect_cart_queue_websocket(websocket: WebSocket) -> None:
    async with _connection_lock:
        _active_websockets.discard(websocket)


async def send_cart_queue_snapshot(websocket: WebSocket) -> None:
    jobs = await list_cart_jobs()
    await websocket.send_json(
        {
            "type": "cart_queue_snapshot",
            "jobs": _serialize_jobs(jobs),
        }
    )


async def broadcast_cart_queue_event(payload: dict) -> None:
    async with _connection_lock:
        websockets = list(_active_websockets)

    disconnected_websockets = []
    for websocket in websockets:
        try:
            await websocket.send_json(payload)
        except Exception:
            disconnected_websockets.append(websocket)

    if disconnected_websockets:
        async with _connection_lock:
            for websocket in disconnected_websockets:
                _active_websockets.discard(websocket)
