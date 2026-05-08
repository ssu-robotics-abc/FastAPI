from pydantic import BaseModel


class ScanRequest(BaseModel):
    barcode_data: str


class ScanResponse(BaseModel):
    product_name: str
    message: str


class QRScanRequest(BaseModel):
    customer_name: str


class QRScanResponse(BaseModel):
    status: str
    message: str
