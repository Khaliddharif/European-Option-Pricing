from backend.app.models.position import Position
from backend.app.portfolio.calculator import calculate_position


def test_long_call_pnl():
    position = Position(
        asset="Call",
        position="Long",
        quantity=100,
        entry_price=5.0,
        maturity=1.0,
        strike=100.0,
        volatility=0.20,
    )

    result = calculate_position(
        position=position,
        spot=100.0,
        rate=0.05,
    )

    assert result.market_value > 0
    assert result.pnl > 0
    assert result.delta > 0
    assert result.gamma > 0
    assert result.vega > 0


def test_short_call_has_negative_greeks():
    position = Position(
        asset="Call",
        position="Short",
        quantity=100,
        entry_price=5.0,
        maturity=1.0,
        strike=100.0,
        volatility=0.20,
    )

    result = calculate_position(
        position=position,
        spot=100.0,
        rate=0.05,
    )

    assert result.delta < 0
    assert result.gamma < 0
    assert result.theta > 0
    assert result.vega < 0


def test_long_future_pnl():
    position = Position(
        asset="Future",
        position="Long",
        quantity=100,
        entry_price=100.0,
    )

    result = calculate_position(
        position=position,
        spot=110.0,
        rate=0.05,
    )

    assert result.pnl == 1000.0
    assert result.delta == 100.0
    assert result.gamma == 0.0
    assert result.theta == 0.0
    assert result.vega == 0.0