import pytest

from backend.app.pricing.black_scholes import option_price
from backend.app.pricing.implied_volatility import implied_volatility


@pytest.mark.parametrize("option_type", ["Call", "Put"])
def test_recovers_volatility_from_different_initial_guesses(option_type):
    expected_volatility = 0.37
    market_price = option_price(
        option_type=option_type,
        spot=100.0,
        strike=105.0,
        volatility=expected_volatility,
        rate=0.04,
        maturity=1.5,
        dividend_yield=0.015,
    )

    for guess in (0.05, 0.20, 0.80, 2.0):
        result = implied_volatility(
            option_type=option_type,
            spot=100.0,
            strike=105.0,
            rate=0.04,
            maturity=1.5,
            dividend_yield=0.015,
            option_value=market_price,
            guess=guess,
        )
        assert result == pytest.approx(expected_volatility, abs=1e-8)


def test_call_implied_volatility():
    volatility = implied_volatility(
        option_type="Call", spot=100.0, strike=100.0, rate=0.05,
        maturity=1.0, dividend_yield=0.0, option_value=10.45058357,
        guess=0.35,
    )
    assert volatility == pytest.approx(0.20, abs=1e-7)


def test_put_implied_volatility():
    volatility = implied_volatility(
        option_type="Put", spot=100.0, strike=100.0, rate=0.05,
        maturity=1.0, dividend_yield=0.0, option_value=5.57352602,
        guess=0.45,
    )
    assert volatility == pytest.approx(0.20, abs=1e-7)


@pytest.mark.parametrize(
    "option_type, option_value",
    [("Call", 100.0), ("Put", 100.0), ("Call", 0.0), ("Put", -1.0)],
)
def test_rejects_prices_outside_no_arbitrage_bounds(option_type, option_value):
    with pytest.raises(ValueError):
        implied_volatility(
            option_type=option_type, spot=100.0, strike=100.0, rate=0.05,
            maturity=1.0, dividend_yield=0.0, option_value=option_value,
        )


def test_rejects_invalid_option_type():
    with pytest.raises(ValueError, match="option_type"):
        implied_volatility(
            option_type="Future", spot=100.0, strike=100.0, rate=0.05,
            maturity=1.0, dividend_yield=0.0, option_value=10.0,
        )


def test_rejects_non_finite_input():
    with pytest.raises(ValueError, match="finite"):
        implied_volatility(
            option_type="Call", spot=float("nan"), strike=100.0, rate=0.05,
            maturity=1.0, dividend_yield=0.0, option_value=10.0,
        )
