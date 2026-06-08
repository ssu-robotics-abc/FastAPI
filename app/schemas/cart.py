from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CartQueueItem(BaseModel):
    id: str = Field(min_length=1)
    amount: int = Field(gt=0)

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("상품 ID는 비어 있을 수 없습니다.")
        return cleaned_value


class CartQueueJob(BaseModel):
    job_id: str
    status: Literal["queued"] = "queued"
    created_at: datetime
    items: list[CartQueueItem]
    total_item_count: int


class CartQueueResponse(BaseModel):
    jobs: list[CartQueueJob]


class CartQueueAcceptedResponse(BaseModel):
    status: str
    message: str
    job: CartQueueJob
