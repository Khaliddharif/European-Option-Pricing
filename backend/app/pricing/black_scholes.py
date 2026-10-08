import math

from scipy.stats import norm


def _validate_inputs(
    spot: float,
    strike: float,
    volatility: float,
    maturity: float,
) -> None:
    """Validate the inputs required by the Black-Scholes model."""

    if spot <= 0:
        raise ValueError("Spot price must be greater than zero.")

    if strike <= 0:
        raise ValueError("Strike price must be greater than zero.")

    if volatility <= 0:
        raise ValueError("Volatility must be greater than zero.")

    if maturity <= 0:
        raise ValueError("Time to maturity must be greater than zero.")


def d1(
    spot: float,
    strike: float,
    volatility: float,
    rate: float,
    maturity: float,
    dividend_yield: float = 0.0,
) -> float:
    """
    Calculate d1 in the Black-Scholes model.
    """

    _validate_inputs(spot, strike, volatility, maturity)

    return (
        math.log(spot / strike)
        + (rate - dividend_yield + 0.5 * volatility**2) * maturity
    ) / (volatility * math.sqrt(maturity))


def d2(
    spot: float,
    strike: float,
    volatility: float,
    rate: float,
    maturity: float,
    dividend_yield: float = 0.0,
) -> float:
    """
    Calculate d2 in the Black-Scholes model.
    """

    return d1(
        spot,
        strike,
        volatility,
        rate,
        maturity,
        dividend_yield,
    ) - volatility * math.sqrt(maturity)


def option_price(
    option_type: str,
    spot: float,
    strike: float,
    volatility: float,
    rate: float,
    maturity: float,
    dividend_yield: float = 0.0,
) -> float:
    """
    Calculate the Black-Scholes price of a European call or put.

    Parameters
    ----------
    option_type:
        "Call" or "Put"
    spot:
        Current underlying price.
    strike:
        Option strike.
    volatility:
        Implied volatility as a decimal.
    rate:
        Risk-free interest rate as a decimal.
    maturity:
        Time to maturity in years.
    dividend_yield:
        Continuous dividend yield as a decimal.
    """

    option_type = option_type.strip().lower()

    if option_type not in {"call", "put"}:
        raise ValueError("option_type must be 'Call' or 'Put'.")

    d1_value = d1(
        spot,
        strike,
        volatility,
        rate,
        maturity,
        dividend_yield,
    )

    d2_value = d2(
        spot,
        strike,
        volatility,
        rate,
        maturity,
        dividend_yield,
    )

    discounted_spot = (
        spot * math.exp(-dividend_yield * maturity)
    )

    discounted_strike = (
        strike * math.exp(-rate * maturity)
    )

    if option_type == "call":
        return (
            discounted_spot * norm.cdf(d1_value)
            - discounted_strike * norm.cdf(d2_value)
        )

    return (
        discounted_strike * norm.cdf(-d2_value)
        - discounted_spot * norm.cdf(-d1_value)
    )


def delta(
    option_type: str,
    spot: float,
    strike: float,
    volatility: float,
    rate: float,
    maturity: float,
    dividend_yield: float = 0.0,
) -> float:
    """
    Calculate option Delta.
    """

    option_type = option_type.strip().lower()

    d1_value = d1(
        spot,
        strike,
        volatility,
        rate,
        maturity,
        dividend_yield,
    )

    if option_type == "call":
        return math.exp(-dividend_yield * maturity) * norm.cdf(d1_value)

    if option_type == "put":
        return math.exp(-dividend_yield * maturity) * (
            norm.cdf(d1_value) - 1
        )

    raise ValueError("option_type must be 'Call' or 'Put'.")


def gamma(
    spot: float,
    strike: float,
    volatility: float,
    rate: float,
    maturity: float,
    dividend_yield: float = 0.0,
) -> float:
    """
    Calculate option Gamma.
    """

    d1_value = d1(
        spot,
        strike,
        volatility,
        rate,
        maturity,
        dividend_yield,
    )

    return (
        math.exp(-dividend_yield * maturity)
        * norm.pdf(d1_value)
        / (spot * volatility * math.sqrt(maturity))
    )


def theta(
    option_type: str,
    spot: float,
    strike: float,
    volatility: float,
    rate: float,
    maturity: float,
    dividend_yield: float = 0.0,
) -> float:
    """
    Calculate daily Theta.

    The original VBA implementation divides Theta by 365,
    so this function returns Theta per calendar day.
    """

    option_type = option_type.strip().lower()

    d1_value = d1(
        spot,
        strike,
        volatility,
        rate,
        maturity,
        dividend_yield,
    )

    d2_value = d2(
        spot,
        strike,
        volatility,
        rate,
        maturity,
        dividend_yield,
    )

    first_term = (
        -math.exp(-dividend_yield * maturity)
        * spot
        * volatility
        * norm.pdf(d1_value)
        / (2 * math.sqrt(maturity))
    )

    if option_type == "call":
        annual_theta = (
            first_term
            - rate
            * strike
            * math.exp(-rate * maturity)
            * norm.cdf(d2_value)
            + dividend_yield
            * spot
            * math.exp(-dividend_yield * maturity)
            * norm.cdf(d1_value)
        )

    elif option_type == "put":
        annual_theta = (
            first_term
            + rate
            * strike
            * math.exp(-rate * maturity)
            * norm.cdf(-d2_value)
            - dividend_yield
            * spot
            * math.exp(-dividend_yield * maturity)
            * norm.cdf(-d1_value)
        )

    else:
        raise ValueError("option_type must be 'Call' or 'Put'.")

    return annual_theta / 365.0


def vega(
    spot: float,
    strike: float,
    volatility: float,
    rate: float,
    maturity: float,
    dividend_yield: float = 0.0,
) -> float:
    """
    Calculate Vega for a 1 percentage-point change in volatility.

    This matches the original VBA implementation, which
    multiplies Vega by 0.01.
    """

    d1_value = d1(
        spot,
        strike,
        volatility,
        rate,
        maturity,
        dividend_yield,
    )

    return (
        0.01
        * spot
        * math.exp(-dividend_yield * maturity)
        * math.sqrt(maturity)
        * norm.pdf(d1_value)
    )


def rho(
    option_type: str,
    spot: float,
    strike: float,
    volatility: float,
    rate: float,
    maturity: float,
    dividend_yield: float = 0.0,
) -> float:
    """
    Calculate Rho for a 1 percentage-point change in rates.
    """

    option_type = option_type.strip().lower()

    d2_value = d2(
        spot,
        strike,
        volatility,
        rate,
        maturity,
        dividend_yield,
    )

    if option_type == "call":
        return (
            0.01
            * strike
            * maturity
            * math.exp(-rate * maturity)
            * norm.cdf(d2_value)
        )

    if option_type == "put":
        return (
            -0.01
            * strike
            * maturity
            * math.exp(-rate * maturity)
            * norm.cdf(-d2_value)
        )

    raise ValueError("option_type must be 'Call' or 'Put'.")