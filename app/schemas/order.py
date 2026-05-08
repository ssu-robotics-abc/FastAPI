from pydantic import BaseModel, Field, field_validator


class PurchaseRequest(BaseModel):
    customer_name: str
    items: dict[str, int] = Field(
        min_length=1,
        description="상품명과 구매 수량의 매핑입니다.",
    )

    @field_validator("items")
    @classmethod
    def validate_quantities(cls, items: dict[str, int]) -> dict[str, int]:
        invalid_items = [name for name, quantity in items.items() if quantity <= 0]
        if invalid_items:
            joined_names = ", ".join(invalid_items)
            raise ValueError(f"구매 수량은 1 이상이어야 합니다: {joined_names}")
        return items


class PurchaseResponse(BaseModel):
    status: str
    order_id: int
    message: str
