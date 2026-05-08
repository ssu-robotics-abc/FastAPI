from sqlalchemy.orm import Session

from app.crud.product import create_product, get_product_by_barcode
from app.db.session import SessionLocal


INITIAL_PRODUCTS = [
    {"barcode_data": "8801117536411", "name": "초코파이", "price": 900, "stock": 30},
    {"barcode_data": "8801062518210", "name": "칸초", "price": 1200, "stock": 20},
    {"barcode_data": "8801062012725", "name": "아몬드 빼빼로", "price": 1000, "stock": 25},
    {"barcode_data": "8801056248703", "name": "펩시", "price": 500, "stock": 50},
    {"barcode_data": "8801097150010", "name": "포카리스웨트", "price": 800, "stock": 40},
    {"barcode_data": "8801121768440", "name": "두유", "price": 1400, "stock": 15},
]


def seed_products(db: Session) -> None:
    for product_data in INITIAL_PRODUCTS:
        existing_product = get_product_by_barcode(db, product_data["barcode_data"])
        if existing_product is None:
            create_product(db, **product_data)

    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        seed_products(db)
    finally:
        db.close()

    print("Initial products seeded.")


if __name__ == "__main__":
    main()
