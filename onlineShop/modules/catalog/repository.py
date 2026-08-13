

from sqlalchemy.orm import Session
from modules.catalog.model import Category, Product


class CategoryRepository:
    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Category | None:
        return (
            db.query(Category).filter(Category.id == category_id).first()
        )

    @staticmethod
    def get_by_name(db: Session, name: str) -> Category | None:
        return (
            db.query(Category).filter(Category.name == name).first()
        )

    @staticmethod
    def list_all(db: Session) -> list[Category]:
        return db.query(Category).order_by(Category.name).all()

    @staticmethod
    def create(db: Session, category: Category) -> Category:
        db.add(category)
        db.commit()
        db.refresh(category)
        return category


class ProductRepository:
    @staticmethod
    def get_by_id(db: Session, product_id: int) -> Product | None:
        return (
            db.query(Product).filter(Product.id == product_id).first()
        )

    @staticmethod
    def get_by_name(db: Session, name: str) -> Product | None:
        return db.query(Product).filter(Product.name == name).first()

    @staticmethod
    def list_active(db: Session) -> list[Product]:
        """Customers see only active products."""
        return (
            db.query(Product)
            .filter(Product.is_active == True)
            .order_by(Product.name)
            .all()
        )

    @staticmethod
    def list_all(db: Session) -> list[Product]:
        """Admin sees all including deactivated."""
        return db.query(Product).order_by(Product.name).all()

    @staticmethod
    def search(
        db: Session,
        name: str | None,
        category: str | None,
    ) -> list[Product]:
        query = db.query(Product).filter(Product.is_active == True)

        if name:
            query = query.filter(Product.name.ilike(f"%{name}%"))
        if category:
            query = query.join(Category).filter(
                Category.name.ilike(f"%{category}%")
            )
        return query.order_by(Product.name).all()

    @staticmethod
    def create(db: Session, product: Product) -> Product:
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def save(db: Session, product: Product) -> Product:
        db.commit()
        db.refresh(product)
        return product
