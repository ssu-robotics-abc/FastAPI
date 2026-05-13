from app.db.base import Base
from app.db.session import engine

# Import models so SQLAlchemy registers all tables before create_all runs.
from app.models import order, product  # noqa: F401


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)