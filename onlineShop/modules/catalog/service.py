
import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.exceptions import AppError
from modules.catalog.model import Category, Product
from modules.catalog.repository import CategoryRepository, ProductRepository
from modules.catalog.schema import (
    CategoryCreate, CategoryUpdate,
    ProductCreate, ProductUpdate,
)

logger = logging.getLogger("online_shopping.catalog")


class CategoryService:
    @staticmethod
    def create(data: CategoryCreate, db: Session) -> Category:
        name = data.name.strip()
        if not name:
            raise AppError(400, "Category name cannot be empty")
        if CategoryRepository.get_by_name(db, name):
            raise AppError(409, "Category already exists")

        try:
            cat = CategoryRepository.create(db, Category(name=name))
            logger.info("CATEGORY CREATED | id=%s | name=%s", cat.id, name)
            return cat
        except IntegrityError as exc:
            db.rollback()
            raise AppError(409, "Category already exists") from exc

    @staticmethod
    def update(
        category_id: int, data: CategoryUpdate, db: Session
    ) -> Category:
        cat = CategoryRepository.get_by_id(db, category_id)
        if not cat:
            raise AppError(404, "Category not found")

        new_name = data.name.strip()
        existing = CategoryRepository.get_by_name(db, new_name)
        if existing and existing.id != category_id:
            raise AppError(409, "Category name already in use")

        cat.name = new_name
        db.commit()
        db.refresh(cat)
        return cat

    @staticmethod
    def list_all(db: Session) -> list[Category]:
        return CategoryRepository.list_all(db)


class ProductService:
    @staticmethod
    def create(data: ProductCreate, db: Session) -> Product:
        name = data.name.strip()
        description = data.description.strip()

        if not name:
            raise AppError(400, "Product name cannot be empty")
        if not description:
            raise AppError(400, "Product description cannot be empty")
        if not CategoryRepository.get_by_id(db, data.category_id):
            raise AppError(404, "Category not found")
        if ProductRepository.get_by_name(db, name):
            raise AppError(409, "Product name already exists")

        product = Product(
            name=name,
            description=description,
            category_id=data.category_id,
            price=data.price,
            available_quantity=data.available_quantity,
            product_url=data.product_url,
        )

        try:
            result = ProductRepository.create(db, product)
            logger.info("PRODUCT CREATED | id=%s | name=%s", result.id, name)
            return result
        except IntegrityError as exc:
            db.rollback()
            raise AppError(409, "Product already exists") from exc

    @staticmethod
    def update(
        product_id: int, data: ProductUpdate, db: Session
    ) -> Product:
        product = ProductRepository.get_by_id(db, product_id)
        if not product:
            raise AppError(404, "Product not found")

        if data.name is not None:
            name = data.name.strip()
            conflict = ProductRepository.get_by_name(db, name)
            if conflict and conflict.id != product_id:
                raise AppError(409, "Product name already in use")
            product.name = name

        if data.description is not None:
            product.description = data.description.strip()
        if data.price is not None:
            product.price = data.price
        if data.available_quantity is not None:
            product.available_quantity = data.available_quantity
        if data.product_url is not None:
            product.product_url = data.product_url
        if data.is_active is not None:
            product.is_active = data.is_active

        result = ProductRepository.save(db, product)
        logger.info("PRODUCT UPDATED | id=%s", product_id)
        return result

    @staticmethod
    def deactivate(product_id: int, db: Session) -> dict:
        product = ProductRepository.get_by_id(db, product_id)
        if not product:
            raise AppError(404, "Product not found")
        product.is_active = False
        db.commit()
        logger.info("PRODUCT DEACTIVATED | id=%s", product_id)
        return {"message": f"Product {product_id} deactivated"}

    @staticmethod
    def get(product_id: int, db: Session) -> Product:
        product = ProductRepository.get_by_id(db, product_id)
        if not product:
            raise AppError(404, "Product not found")
        return product

    @staticmethod
    def list_active(db: Session) -> list[Product]:
        return ProductRepository.list_active(db)

    @staticmethod
    def search(
        name: str | None, category: str | None, db: Session
    ) -> list[Product]:
        return ProductRepository.search(db, name, category)
