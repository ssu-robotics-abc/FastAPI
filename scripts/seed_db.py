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
    {
        "barcode_data": "8801117536411",
        "name": "chocopie",
        "name_ko": "초코파이",
        "image_url": "https://placehold.co/480x360/f8fafc/191f28?text=Chocopie",
        "price": 900,
        "weight_grams": 39,
        "stock": 30,
        "rating_average": 4.6,
        "rating_count": 128,
        "category": "snack",
    },
    {
        "barcode_data": "8801062518210",
        "name": "Kancho",
        "name_ko": "칸초",
        "image_url": "https://placehold.co/480x360/f8fafc/191f28?text=Kancho",
        "price": 1200,
        "weight_grams": 54,
        "stock": 20,
        "rating_average": 4.4,
        "rating_count": 96,
        "category": "snack",
    },
    {
        "barcode_data": "8801062012725",
        "name": "pepero_almond",
        "name_ko": "아몬드 빼빼로",
        "image_url": "https://placehold.co/480x360/f8fafc/191f28?text=Pepero",
        "price": 1000,
        "weight_grams": 37,
        "stock": 25,
        "rating_average": 4.7,
        "rating_count": 151,
        "category": "snack",
    },
    {
        "barcode_data": "8801056248703",
        "name": "pepsi",
        "name_ko": "펩시",
        "image_url": "https://placehold.co/480x360/f8fafc/191f28?text=Pepsi",
        "price": 500,
        "weight_grams": 250,
        "stock": 50,
        "rating_average": 4.2,
        "rating_count": 73,
        "category": "drink",
    },
    {
        "barcode_data": "8801097150010",
        "name": "pocarisweat",
        "name_ko": "포카리스웨트",
        "image_url": "https://placehold.co/480x360/f8fafc/191f28?text=Pocari",
        "price": 800,
        "weight_grams": 245,
        "stock": 40,
        "rating_average": 4.8,
        "rating_count": 188,
        "category": "drink",
    },
    {
        "barcode_data": "8801121768440",
        "name": "soy_milk",
        "name_ko": "두유",
        "image_url": "https://placehold.co/480x360/f8fafc/191f28?text=Soy+Milk",
        "price": 1400,
        "weight_grams": 190,
        "stock": 15,
        "rating_average": 4.3,
        "rating_count": 64,
        "category": "drink",
    },
]


def seed_products(db: Session) -> None:
    for product_data in INITIAL_PRODUCTS:
        existing_product = get_product_by_barcode(db, product_data["barcode_data"])
        if existing_product is None:
            create_product(db, **product_data)
        else:
            for key, value in product_data.items():
                setattr(existing_product, key, value)

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
