from sqlalchemy.orm import Session

from app.models.product import Product


def get_product_by_name(db: Session, product_name: str) -> Product | None:
    return db.query(Product).filter(Product.name == product_name).first()


def get_product_by_id(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_barcode(db: Session, barcode_data: str) -> Product | None:
    return db.query(Product).filter(Product.barcode_data == barcode_data).first()


def create_product(
    db: Session,
    *,
    barcode_data: str,
    name: str,
    price: int,
    stock: int,
    name_ko: str | None = None,
    image_url: str | None = None,
    weight_grams: int | None = None,
    rating_average: float | None = None,
    rating_count: int = 0,
    category: str | None = None,
) -> Product:
    product = Product(
        barcode_data=barcode_data,
        name=name,
        price=price,
        stock=stock,
        name_ko=name_ko,
        image_url=image_url,
        weight_grams=weight_grams,
        rating_average=rating_average,
        rating_count=rating_count,
        category=category,
    )
    db.add(product)
    return product


def decrease_stock(product: Product, quantity: int) -> None:
    product.stock -= quantity


def list_products(db: Session) -> list[Product]:
    return db.query(Product).order_by(Product.id).all()
