from backend.app.pricing.implied_volatility import (
    implied_volatility,
)


def test_call_implied_volatility():
    volatility = implied_volatility(
        option_type="Call",
        spot=100.0,
        strike=100.0,
        rate=0.05,
        maturity=1.0,
        dividend_yield=0.0,
        option_value=10.45058357,
        guess=0.20,
    )

    assert abs(volatility - 0.20) < 1e-5


def test_put_implied_volatility():
    volatility = implied_volatility(
        option_type="Put",
        spot=100.0,
        strike=100.0,
        rate=0.05,
        maturity=1.0,
        dividend_yield=0.0,
        option_value=5.57352602,
        guess=0.20,
    )

    assert abs(volatility - 0.20) < 1e-5