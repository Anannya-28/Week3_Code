
from unittest.mock import MagicMock, patch
import pytest
from core.exceptions import AppError
from modules.orders.service import OrderService


class TestOrderServiceSync:
    """Tests for sync order service methods (history, details, list_all)."""

    def test_history_user_not_found_raises_404(self):
        db = MagicMock()

        with patch(
            "modules.orders.service.UserRepository.get_by_id",
            return_value=None,
        ):
            with pytest.raises(AppError) as exc_info:
                OrderService.history(999, db)

        assert exc_info.value.status_code == 404

    def test_history_returns_orders_for_user(self):
        db = MagicMock()
        mock_orders = [MagicMock(id=1), MagicMock(id=2)]

        with patch(
            "modules.orders.service.UserRepository.get_by_id",
            return_value=MagicMock(),
        ), patch(
            "modules.orders.service.OrderRepository.list_for_user",
            return_value=mock_orders,
        ):
            result = OrderService.history(1, db)

        assert len(result) == 2

    def test_details_not_found_raises_404(self):
        db = MagicMock()

        with patch(
            "modules.orders.service.OrderRepository.get_by_id",
            return_value=None,
        ):
            with pytest.raises(AppError) as exc_info:
                OrderService.details(999, db)

        assert exc_info.value.status_code == 404

    def test_details_returns_order(self):
        db = MagicMock()
        mock_order = MagicMock(id=5)

        with patch(
            "modules.orders.service.OrderRepository.get_by_id",
            return_value=mock_order,
        ):
            result = OrderService.details(5, db)

        assert result.id == 5

    def test_list_all_returns_all_orders(self):
        db = MagicMock()
        mock_orders = [MagicMock(), MagicMock(), MagicMock()]

        with patch(
            "modules.orders.service.OrderRepository.list_all",
            return_value=mock_orders,
        ):
            result = OrderService.list_all(db)

        assert len(result) == 3
