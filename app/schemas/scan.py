from pydantic import BaseModel


class ScanRequest(BaseModel):
    barcode_data: str


class ScanResponse(BaseModel):
    product_name: str
    message: str
