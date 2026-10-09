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

def test_portfolio_totals_equal_sum_of_individual_position_results():
    from backend.app.portfolio.calculator import calculate_position

    positions = [
        Position(
            asset="Call", position="Long", quantity=2, entry_price=7.0,
            maturity=1.5, strike=100.0, volatility=0.24,
        ),
        Position(
            asset="Put", position="Short", quantity=3, entry_price=5.0,
            maturity=0.8, strike=95.0, volatility=0.21,
        ),
        Position(
            asset="Future", position="Long", quantity=1, entry_price=98.0,
        ),
    ]
    spot, rate, dividend_yield = 102.0, 0.035, 0.01
    results = [
        calculate_position(p, spot, rate, dividend_yield)
        for p in positions
    ]
    portfolio = calculate_portfolio(
        positions, spot, rate, dividend_yield
    )

    for field in ("market_value", "pnl", "delta", "gamma", "theta", "vega"):
        expected = sum(getattr(item, field) for item in results)
        assert abs(getattr(portfolio, field) - expected) < 1e-10
