import pytest
from fastapi.testclient import TestClient
from backend.app.api.main import app
from backend.app.models.position import Position
from backend.app.portfolio.calculator import calculate_position

client = TestClient(app)


def test_future_multiplier_scales_pnl_notional_and_delta():
    p = Position(asset="Future", position="Long", quantity=2, entry_price=100,
                 contract_multiplier=50, currency="EUR")
    result = calculate_position(p, spot=103, rate=0.03)
    assert result.pnl == pytest.approx(300)
    assert result.market_value == pytest.approx(10300)
    assert result.delta == pytest.approx(100)


def test_short_future_multiplier_scales_pnl_and_delta_with_correct_sign():
    p = Position(asset="Future", position="Short", quantity=3, entry_price=105,
                 contract_multiplier=10, currency="USD")
    result = calculate_position(p, spot=100, rate=0.03)
    assert result.pnl == pytest.approx(150)
    assert result.market_value == pytest.approx(-3000)
    assert result.delta == pytest.approx(-30)


def test_margin_is_aggregated_per_contract_and_multiplier_does_not_scale_margin():
    p = Position(asset="Future", position="Long", quantity=4, entry_price=100,
                 contract_multiplier=25, initial_margin=1200, maintenance_margin=900)
    result = calculate_position(p, spot=100, rate=0.03)
    assert result.initial_margin == pytest.approx(4800)
    assert result.maintenance_margin == pytest.approx(3600)


def test_invalid_margin_relationship_is_rejected():
    with pytest.raises(ValueError, match="Maintenance margin"):
        Position(asset="Future", position="Long", quantity=1, entry_price=100,
                 initial_margin=500, maintenance_margin=600)


def test_portfolio_endpoint_accepts_futures_contract_metadata():
    response = client.post("/portfolio", json={
        "positions": [{"asset": "Future", "position": "Long", "quantity": 2,
                       "entry_price": 100, "contract_multiplier": 50,
                       "expiry_month": "Dec 2026", "currency": "EUR",
                       "tick_size": 0.5, "tick_value": 25,
                       "initial_margin": 1000, "maintenance_margin": 800,
                       "settlement_convention": "Daily mark-to-market"}],
        "spot": 103, "rate": 0.03,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["pnl"] == pytest.approx(300)
    assert data["initial_margin"] == pytest.approx(2000)
    assert data["maintenance_margin"] == pytest.approx(1600)
