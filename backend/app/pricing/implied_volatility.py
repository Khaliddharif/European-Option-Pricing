"""Robust implied-volatility solver for European options under Black-Scholes.

All rates, dividend yields, and volatilities are expressed as decimals
(e.g. 0.20 means 20%). Option values use the same units as spot and strike.
"""

import math

from scipy.optimize import brentq

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
    """Return the Black-Scholes implied volatility as a decimal.

    ``guess`` and ``d_vol`` are retained for backwards compatibility with the
    previous function signature. The bracketed Brent solver does not depend on
    the initial guess or finite-difference step, which avoids Newton iteration
    instability for low-vega options.

    Raises:
        ValueError: If inputs are invalid, the market price violates European
            no-arbitrage bounds, or a root cannot be found in the search range.
    """
    normalized_type = option_type.strip().lower() if isinstance(option_type, str) else ""
    if normalized_type not in {"call", "put"}:
        raise ValueError("option_type must be 'Call' or 'Put'.")

    numeric_inputs = {
        "spot": spot,
        "strike": strike,
        "rate": rate,
        "maturity": maturity,
        "dividend_yield": dividend_yield,
        "option_value": option_value,
        "guess": guess,
        "d_vol": d_vol,
        "epsilon": epsilon,
    }
    for name, value in numeric_inputs.items():
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number.")

    if spot <= 0:
        raise ValueError("Spot price must be greater than zero.")
    if strike <= 0:
        raise ValueError("Strike price must be greater than zero.")
    if maturity <= 0:
        raise ValueError("Time to maturity must be greater than zero.")
    if option_value <= 0:
        raise ValueError("Option value must be greater than zero.")
    if guess <= 0:
        raise ValueError("Initial volatility guess must be greater than zero.")
    if d_vol <= 0:
        raise ValueError("d_vol must be greater than zero.")
    if epsilon <= 0:
        raise ValueError("epsilon must be greater than zero.")
    if max_iterations < 1:
        raise ValueError("max_iterations must be at least 1.")

    discounted_spot = spot * math.exp(-dividend_yield * maturity)
    discounted_strike = strike * math.exp(-rate * maturity)
    if normalized_type == "call":
        lower_bound = max(discounted_spot - discounted_strike, 0.0)
        upper_bound = discounted_spot
    else:
        lower_bound = max(discounted_strike - discounted_spot, 0.0)
        upper_bound = discounted_strike

    # A finite positive volatility produces a price strictly between these
    # theoretical bounds. Tolerance scales with the underlying price units.
    price_tolerance = max(1e-12, 1e-12 * max(spot, strike, option_value))
    if option_value < lower_bound - price_tolerance:
        raise ValueError(
            f"Option value is below the European no-arbitrage lower bound "
            f"({lower_bound:.12g})."
        )
    if option_value > upper_bound + price_tolerance:
        raise ValueError(
            f"Option value is above the European no-arbitrage upper bound "
            f"({upper_bound:.12g})."
        )
    if option_value <= lower_bound + price_tolerance:
        raise ValueError(
            "Option value is at or too close to the lower no-arbitrage bound; "
            "a finite implied volatility cannot be determined reliably."
        )
    if option_value >= upper_bound - price_tolerance:
        raise ValueError(
            "Option value is at or too close to the upper no-arbitrage bound; "
            "implied volatility is unbounded or numerically unstable."
        )

    def price_error(volatility: float) -> float:
        return option_price(
            option_type=normalized_type,
            spot=spot,
            strike=strike,
            volatility=volatility,
            rate=rate,
            maturity=maturity,
            dividend_yield=dividend_yield,
        ) - option_value

    low_vol = 1e-8
    high_vol = max(1.0, min(float(guess) * 2.0, 5.0))
    low_error = price_error(low_vol)
    high_error = price_error(high_vol)

    # Expand the upper bracket when necessary. The bound check above prevents
    # chasing prices that cannot be attained by any finite volatility.
    while low_error * high_error > 0 and high_vol < 10.0:
        high_vol = min(high_vol * 2.0, 10.0)
        high_error = price_error(high_vol)

    if low_error * high_error > 0:
        raise ValueError(
            "Could not bracket implied volatility in the supported range "
            "(0, 10]. Check the market price and inputs."
        )

    try:
        result = brentq(
            price_error,
            low_vol,
            high_vol,
            xtol=max(1e-12, min(epsilon, 1e-8)),
            rtol=1e-12,
            maxiter=max_iterations,
        )
    except (ValueError, RuntimeError) as exc:
        raise ValueError(
            f"Implied volatility solver failed to converge: {exc}"
        ) from exc

    if not math.isfinite(result) or result <= 0:
        raise ValueError("Implied volatility solver returned an invalid result.")
    return float(result)
