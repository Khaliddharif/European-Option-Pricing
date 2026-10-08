import pytest

from backend.app.models.position import Position


def test_valid_call_position():
    position = Position(
        asset="Call",
        position="Long",
        quantity=100,
        entry_price=5.0,
        maturity=1.0,
        strike=100.0,
        volatility=0.20,
    )

    assert position.asset == "Call"
    assert position.position == "Long"
    assert position.quantity == 100


def test_valid_future_position():
    position = Position(
        asset="Future",
        position="Long",
        quantity=100,
        entry_price=100.0,
    )

    assert position.asset == "Future"


def test_option_requires_strike():
    with pytest.raises(ValueError):
        Position(
            asset="Call",
            position="Long",
            quantity=100,
            entry_price=5.0,
            maturity=1.0,
            volatility=0.20,
        )


def test_quantity_must_be_positive():
    with pytest.raises(ValueError):
        Position(
            asset="Call",
            position="Long",
            quantity=0,
            entry_price=5.0,
            maturity=1.0,
            strike=100.0,
            volatility=0.20,
        )