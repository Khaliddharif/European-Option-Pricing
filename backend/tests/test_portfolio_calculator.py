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

def test_short_call_pnl_is_opposite_of_long_call():
    common = dict(
        asset="Call",
        quantity=3,
        entry_price=4.0,
        maturity=1.0,
        strike=100.0,
        volatility=0.25,
    )
    long_result = calculate_position(
        Position(position="Long", **common), spot=110.0, rate=0.03
    )
    short_result = calculate_position(
        Position(position="Short", **common), spot=110.0, rate=0.03
    )

    assert short_result.market_value == -long_result.market_value
    assert short_result.pnl == -long_result.pnl
    assert short_result.delta == -long_result.delta
    assert short_result.gamma == -long_result.gamma
    assert short_result.theta == -long_result.theta
    assert short_result.vega == -long_result.vega


def test_short_future_pnl_and_delta_have_correct_sign():
    position = Position(
        asset="Future",
        position="Short",
        quantity=4,
        entry_price=105.0,
    )
    result = calculate_position(position=position, spot=100.0, rate=0.03)

    assert result.market_value == -400.0
    assert result.pnl == 20.0
    assert result.delta == -4.0
    assert result.gamma == result.theta == result.vega == 0.0


def test_option_greeks_scale_linearly_with_quantity():
    base = dict(
        asset="Put",
        position="Long",
        entry_price=6.0,
        maturity=0.75,
        strike=105.0,
        volatility=0.22,
    )
    one = calculate_position(
        Position(quantity=1, **base), spot=100.0, rate=0.04
    )
    five = calculate_position(
        Position(quantity=5, **base), spot=100.0, rate=0.04
    )

    for field in ("market_value", "pnl", "delta", "gamma", "theta", "vega"):
        assert abs(getattr(five, field) - 5 * getattr(one, field)) < 1e-10
