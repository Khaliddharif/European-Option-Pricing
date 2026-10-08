from backend.app.pricing.black_scholes import option_price


def implied_volatility(
    option_type: str,
    spot: float,
    strike: float,
    rate: float,
    maturity: float,
    dividend_yield: float,
    option_value: float,
    guess: float = 0.20,
    d_vol: float = 0.00001,
    epsilon: float = 0.00001,
    max_iterations: int = 100,
) -> float:
    """
    Calculate implied volatility using the same Newton-style
    finite-difference approach as the original VBA model.

    Parameters
    ----------
    option_type:
        "Call" or "Put".

    spot:
        Current underlying price.

    strike:
        Option strike price.

    rate:
        Risk-free interest rate as a decimal.

    maturity:
        Time to maturity in years.

    dividend_yield:
        Continuous dividend yield as a decimal.

    option_value:
        Observed market option value.

    guess:
        Initial volatility estimate.

    d_vol:
        Volatility perturbation used to estimate the price slope.

    epsilon:
        Convergence tolerance.

    max_iterations:
        Maximum number of iterations.

    Returns
    -------
    float
        Implied volatility as a decimal.
    """

    if option_value <= 0:
        raise ValueError("Option value must be greater than zero.")

    if guess <= 0:
        raise ValueError("Initial volatility guess must be greater than zero.")

    if d_vol <= 0:
        raise ValueError("d_vol must be greater than zero.")

    vol_1 = guess

    value_1 = option_price(
        option_type=option_type,
        spot=spot,
        strike=strike,
        volatility=vol_1,
        rate=rate,
        maturity=maturity,
        dividend_yield=dividend_yield,
    )

    dx = 1.0

    iteration = 1

    while (
        iteration <= max_iterations
        and abs(dx) >= epsilon
        and abs(option_value - value_1) > epsilon
    ):
        value_1 = option_price(
            option_type=option_type,
            spot=spot,
            strike=strike,
            volatility=vol_1,
            rate=rate,
            maturity=maturity,
            dividend_yield=dividend_yield,
        )

        vol_2 = vol_1 - d_vol

        value_2 = option_price(
            option_type=option_type,
            spot=spot,
            strike=strike,
            volatility=vol_2,
            rate=rate,
            maturity=maturity,
            dividend_yield=dividend_yield,
        )

        dx = (value_2 - value_1) / d_vol

        if abs(dx) < 1e-12:
            raise ValueError(
                "Implied volatility calculation failed: "
                "price sensitivity to volatility is too small."
            )

        vol_1 = vol_1 - (option_value - value_1) / dx

        if vol_1 <= 0:
            raise ValueError(
                "Implied volatility calculation produced "
                "a non-positive volatility."
            )

        iteration += 1

    if abs(option_value - value_1) > epsilon:
        raise ValueError(
            "Implied volatility did not converge within "
            f"{max_iterations} iterations."
        )

    return vol_1