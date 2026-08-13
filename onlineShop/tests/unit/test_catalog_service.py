

from unittest.mock import MagicMock, patch

import pytest

from core.exceptions import AppError
from modules.catalog.schema import ProductCreate, ProductUpdate
from modules.catalog.service import ProductService
from decimal import Decimal


class TestProductService:

    def test_create_product_success(self):
        db = MagicMock()
        data = ProductCreate(
            name="Laptop",
            description="A good laptop",
            category_id=1,
            price=Decimal("999.00"),
            available_quantity=5,
        )

        mock_product = MagicMock()          
        mock_product.id = 1                 
        mock_product.name = "Laptop"       

        with patch(
            "modules.catalog.service.CategoryRepository.get_by_id",
            return_value=MagicMock(),
        ), patch(
            "modules.catalog.service.ProductRepository.get_by_name",
            return_value=None,
        ), patch(
            "modules.catalog.service.ProductRepository.create",
            return_value=mock_product,
        ):
            result = ProductService.create(data, db)  

        assert result.name == "Laptop"
        assert result.id == 1

    def test_create_product_duplicate_raises_409(self):
        db = MagicMock()
        data = ProductCreate(
            name="Laptop",
            description="Duplicate",
            category_id=1,
            price=Decimal("999.00"),
            available_quantity=5,
        )

        with patch(
            "modules.catalog.service.CategoryRepository.get_by_id",
            return_value=MagicMock(),
        ), patch(
            "modules.catalog.service.ProductRepository.get_by_name",
            return_value=MagicMock(),  
        ):
            with pytest.raises(AppError) as exc_info:
                ProductService.create(data, db)

        assert exc_info.value.status_code == 409

    def test_create_product_category_not_found_raises_404(self):
        db = MagicMock()
        data = ProductCreate(
            name="Phone",
            description="Smartphone",
            category_id=999,
            price=Decimal("500.00"),
            available_quantity=10,
        )

        with patch(
            "modules.catalog.service.CategoryRepository.get_by_id",
            return_value=None,   
        ):
            with pytest.raises(AppError) as exc_info:
                ProductService.create(data, db)

        assert exc_info.value.status_code == 404

    def test_deactivate_product_success(self):
        db = MagicMock()
        mock_product = MagicMock()
        mock_product.is_active = True

        with patch(
            "modules.catalog.service.ProductRepository.get_by_id",
            return_value=mock_product,
        ):
            result = ProductService.deactivate(1, db)

        assert mock_product.is_active is False
        assert "deactivated" in result["message"]

    def test_deactivate_nonexistent_product_raises_404(self):
        db = MagicMock()

        with patch(
            "modules.catalog.service.ProductRepository.get_by_id",
            return_value=None,
        ):
            with pytest.raises(AppError) as exc_info:
                ProductService.deactivate(999, db)

        assert exc_info.value.status_code == 404         
