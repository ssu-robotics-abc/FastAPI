from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import Dict
import datetime

# ==========================================
# 1. 데이터베이스 설정 (SQLite)
# ==========================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./robot_orders.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# 2. DB 테이블 모델 정의
# ==========================================
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    barcode_data = Column(Integer, unique=True, index=True)
    name = Column(String)
    price = Column(Integer)
    stock = Column(Integer, default=20)

    items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    purchase_time = Column(DateTime, default=datetime.datetime.utcnow)
    customer = Column(String)

    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="items")

Base.metadata.create_all(bind=engine)

# ==========================================
# 3. FastAPI 앱 및 초기 데이터 설정
# ==========================================
app = FastAPI(title="로보틱스 스토어 서버")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_populate_db():
    db = SessionLocal()
    initial_products = [
        {"barcode_data": 8801117536411, "name": "초코파이", "price": 900, "stock": 30},
        {"barcode_data": 8801062518210, "name": "칸초", "price": 1200, "stock": 20},
        {"barcode_data": 8801062012725, "name": "아몬드 빼빼로", "price": 1000, "stock": 25},
        {"barcode_data": 8801056248703, "name": "펩시", "price": 500, "stock": 50},
        {"barcode_data": 8801097150010, "name": "포카리스웨트", "price": 800, "stock": 40},
        {"barcode_data": 8801121768440, "name": "두유", "price": 1400, "stock": 15}
    ]
    for p in initial_products:
        if not db.query(Product).filter(Product.barcode_data == p["barcode_data"]).first():
            db.add(Product(**p))
    db.commit()
    db.close()

# ==========================================
# 4. Pydantic 스키마 (데이터 검증용)
# ==========================================
class ScanRequest(BaseModel):
    barcode_data: int

class PurchaseRequest(BaseModel):
    customer_name: str
    items: Dict[str, int]

class QRScanRequest(BaseModel):
    customer_name: str

# ==========================================
# 5. API 엔드포인트
# ==========================================

# 1. 상품 재고 및 바코드 조회
@app.get("/stock/{product_name}")
def get_product_stock(product_name: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.name == product_name).first()
    if not product:
        raise HTTPException(status_code=404, detail="해당 상품을 찾을 수 없습니다.")
    return {"product_name": product.name, 
            "remaining_stock": product.stock,
            "barcode_data": product.barcode_data}

# 2. 바코드 숫자 정보 전송 및 ROS2 스캔 신호
@app.post("/scan")
def process_barcode_scan(request: ScanRequest, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.barcode_data == request.barcode_data).first()
    if not product:
        raise HTTPException(status_code=404, detail="등록되지 않은 바코드입니다.")

    # ----------------------------------------------------
    # [ROS 2 연동] TODO: 바코드 스캔 완료 신호 전송 로직
    # 예시: ros_node.publish_scan_event(product.name)
    # ----------------------------------------------------

    return {"product_name": product.name, "message": "스캔 완료 신호가 전송되었습니다."}

# 3. 장바구니 결제 및 ROS2 명령
@app.post("/purchase")
def process_purchase(request: PurchaseRequest, db: Session = Depends(get_db)):
    for product_name, qty in request.items.items():
        product = db.query(Product).filter(Product.name == product_name).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"'{product_name}' 상품을 찾을 수 없습니다.")
        if product.stock < qty:
            raise HTTPException(status_code=400, detail=f"'{product_name}' 재고가 부족합니다. (현재: {product.stock}개)")

    new_order = Order(customer=request.customer_name)
    db.add(new_order)
    db.flush()

    for product_name, qty in request.items.items():
        product = db.query(Product).filter(Product.name == product_name).first()
        product.stock -= qty 
        new_item = OrderItem(order_id=new_order.id, product_id=product.id, quantity=qty)
        db.add(new_item)

    db.commit()

    # ----------------------------------------------------
    # [ROS 2 연동] TODO: 구매 완료 및 로봇 동작 신호 전송 로직
    # 예시: ros_node.publish_purchase_complete(new_order.id, request.items)
    # ----------------------------------------------------

    return {
        "status": "success",
        "order_id": new_order.id,
        "message": f"구매 처리가 완료되었습니다. (구매자: {request.customer_name})"
    }

# 4. [NEW] 구매자 QR 스캔 완료 ROS 2 신호 전송
@app.post("/qr_scan_complete")
def process_qr_scan_complete(request: QRScanRequest):
    # ----------------------------------------------------
    # [ROS 2 연동] TODO: 특정 사용자의 QR 코드 인식 완료 신호 전송 로직
    # 예시: ros_node.publish_qr_scan_complete(request.customer_name)
    # ----------------------------------------------------

    return {
        "status": "success",
        "message": f"[{request.customer_name}]님의 QR 스캔 완료 신호가 ROS 2로 전송되었습니다."
    }