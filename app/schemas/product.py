from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    barcode_data: str
    name: str
    price: int
    stock: int


class ProductRead(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProductDisplayRead(ProductRead):
    name_ko: str
    image_url: str | None = None
    weight_grams: int | None = None
    price_per_gram: float | None = None
    rating_average: float | None = None
    rating_count: int = 0
    category: str | None = None

    @classmethod
    def from_product(cls, product: Any) -> "ProductDisplayRead":
        price_per_gram = None
        if product.weight_grams:
            price_per_gram = round(product.price / product.weight_grams, 2)

        return cls(
            id=product.id,
            barcode_data=product.barcode_data,
            name=product.name,
            name_ko=product.name_ko or product.name,
            image_url=product.image_url,
            price=product.price,
            stock=product.stock,
            weight_grams=product.weight_grams,
            price_per_gram=price_per_gram,
            rating_average=product.rating_average,
            rating_count=product.rating_count,
            category=product.category,
        )


class ProductStockUpdate(BaseModel):
    stock: int = Field(ge=0)


class StockResponse(BaseModel):
    product_name: str
    remaining_stock: int
    barcode_data: str
