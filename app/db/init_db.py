from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine

# Import models so SQLAlchemy registers all tables before create_all runs.
from app.models import order, product  # noqa: F401


PRODUCT_DISPLAY_COLUMNS = {
    "name_ko": "VARCHAR",
    "image_url": "VARCHAR",
    "weight_grams": "INTEGER",
    "rating_average": "FLOAT",
    "rating_count": "INTEGER NOT NULL DEFAULT 0",
    "category": "VARCHAR",
}


def ensure_product_display_columns() -> None:
    """Add v2 display fields when an existing SQLite DB predates them."""

    if engine.dialect.name != "sqlite":
        return

    with engine.begin() as connection:
        existing_columns = {
            row[1]
            for row in connection.execute(text("PRAGMA table_info(products)"))
        }
        for column_name, column_type in PRODUCT_DISPLAY_COLUMNS.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(f"ALTER TABLE products ADD COLUMN {column_name} {column_type}")
                )


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_product_display_columns()
