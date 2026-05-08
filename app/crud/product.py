from sqlalchemy.orm import Session

from app.models.product import Product


def get_product_by_name(db: Session, product_name: str) -> Product | None:
    return db.query(Product).filter(Product.name == product_name).first()


def get_product_by_barcode(db: Session, barcode_data: str) -> Product | None:
    return db.query(Product).filter(Product.barcode_data == barcode_data).first()


def create_product(
    db: Session,
    *,
    barcode_data: str,
    name: str,
    price: int,
    stock: int,
) -> Product:
    product = Product(
        barcode_data=barcode_data,
        name=name,
        price=price,
        stock=stock,
    )
    db.add(product)
    return product


def decrease_stock(product: Product, quantity: int) -> None:
    product.stock -= quantity
