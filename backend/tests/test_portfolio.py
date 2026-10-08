from backend.app.models.position import Position
from backend.app.portfolio.portfolio import calculate_portfolio


def test_portfolio_combines_multiple_positions():
    positions = [
        Position(
            asset="Call",
            position="Long",
            quantity=100,
            entry_price=5.0,
            maturity=1.0,
            strike=100.0,
            volatility=0.20,
        ),
        Position(
            asset="Put",
            position="Long",
            quantity=50,
            entry_price=4.0,
            maturity=1.0,
            strike=100.0,
            volatility=0.20,
        ),
    ]

    result = calculate_portfolio(
        positions=positions,
        spot=100.0,
        rate=0.05,
    )

    assert result.market_value > 0
    assert result.pnl > 0
    assert result.delta != 0
    assert result.gamma > 0
    assert result.vega > 0


def test_empty_portfolio_returns_zeroes():
    result = calculate_portfolio(
        positions=[],
        spot=100.0,
        rate=0.05,
    )

    assert result.market_value == 0
    assert result.pnl == 0
    assert result.delta == 0
    assert result.gamma == 0
    assert result.theta == 0
    assert result.vega == 0