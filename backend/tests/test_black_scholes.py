from backend.app.pricing.black_scholes import (
    option_price,
    delta,
    gamma,
)


def test_call_price():
    price = option_price(
        option_type="Call",
        spot=100.0,
        strike=100.0,
        volatility=0.20,
        rate=0.05,
        maturity=1.0,
        dividend_yield=0.0,
    )

    assert abs(price - 10.45058357) < 1e-6


def test_put_price():
    price = option_price(
        option_type="Put",
        spot=100.0,
        strike=100.0,
        volatility=0.20,
        rate=0.05,
        maturity=1.0,
        dividend_yield=0.0,
    )

    assert abs(price - 5.57352602) < 1e-6


def test_call_delta():
    result = delta(
        "Call",
        100.0,
        100.0,
        0.20,
        0.05,
        1.0,
    )

    assert abs(result - 0.63683065) < 1e-6


def test_gamma():
    result = gamma(
        100.0,
        100.0,
        0.20,
        0.05,
        1.0,
    )

    assert abs(result - 0.01876202) < 1e-6




def test_black_scholes_benchmark_matches_expected_values():
    from backend.app.pricing.black_scholes import (
        option_price,
        delta,
        gamma,
        theta,
        vega,
    )

    spot = 100.0
    strike = 100.0
    rate = 0.05
    maturity = 1.0
    volatility = 0.20

    assert abs(
        option_price(
            option_type="Call",
            spot=spot,
            strike=strike,
            volatility=volatility,
            rate=rate,
            maturity=maturity,
        ) - 10.45058357
    ) < 1e-6

    assert abs(
        delta(
            option_type="Call",
            spot=spot,
            strike=strike,
            volatility=volatility,
            rate=rate,
            maturity=maturity,
        ) - 0.63683065
    ) < 1e-6

    assert abs(
        gamma(
            spot=spot,
            strike=strike,
            volatility=volatility,
            rate=rate,
            maturity=maturity,
        ) - 0.01876202
    ) < 1e-6

    assert theta(
        option_type="Call",
        spot=spot,
        strike=strike,
        volatility=volatility,
        rate=rate,
        maturity=maturity,
    ) < 0

    assert vega(
        spot=spot,
        strike=strike,
        volatility=volatility,
        rate=rate,
        maturity=maturity,
    ) > 0