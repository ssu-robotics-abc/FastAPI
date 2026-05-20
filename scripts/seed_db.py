from pathlib import Path
import sys

from sqlalchemy.orm import Session


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.crud.product import create_product, get_product_by_barcode
from app.db.init_db import initialize_database
from app.db.session import SessionLocal


INITIAL_PRODUCTS = [
    {"barcode_data": "8801117536411", "name": "chocopie", "price": 900, "stock": 30},
    {"barcode_data": "8801062518210", "name": "Kancho", "price": 1200, "stock": 20},
    {"barcode_data": "8801062012725", "name": "pepero_almond", "price": 1000, "stock": 25},
    {"barcode_data": "8801056248703", "name": "pepsi", "price": 500, "stock": 50},
    {"barcode_data": "8801097150010", "name": "pocarisweat", "price": 800, "stock": 40},
    {"barcode_data": "8801121768440", "name": "soy_milk", "price": 1400, "stock": 15},
]


def seed_products(db: Session) -> None:
    for product_data in INITIAL_PRODUCTS:
        existing_product = get_product_by_barcode(db, product_data["barcode_data"])
        if existing_product is None:
            create_product(db, **product_data)

    db.commit()


def main() -> None:
    initialize_database()

    db = SessionLocal()
    try:
        seed_products(db)
    finally:
        db.close()

    print("Initial products seeded.")


if __name__ == "__main__":
    main()
