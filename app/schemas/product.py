from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    barcode_data: str
    name: str
    price: int
    stock: int


class ProductRead(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StockResponse(BaseModel):
    product_name: str
    remaining_stock: int
    barcode_data: str
