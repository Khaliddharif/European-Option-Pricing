from backend.app.pricing.black_scholes import (
    option_price,
    delta,
    gamma,
    theta,
    vega,
)


SPOT_VARIATIONS = [-0.20, -0.10, 0.00, 0.10, 0.20]
VOLATILITY_VARIATIONS = [-0.10, -0.05, 0.00, 0.05, 0.10]


def generate_spot_scenarios(
    spot: float,
    min_change: float = -0.20,
    max_change: float = 0.20,
    step: float = 0.10,
) -> list[float]:
    """
    Generate spot-price scenarios using percentage changes.

    Example:
        spot = 100
        -> [80, 90, 100, 110, 120]
    """
    scenarios = []
    current = min_change

    while current <= max_change + 1e-9:
        scenarios.append(round(spot * (1 + current), 10))
        current += step

    return scenarios


def generate_volatility_scenarios(
    volatility: float,
    min_change: float = -0.10,
    max_change: float = 0.10,
    step: float = 0.05,
) -> list[float]:
    """
    Generate implied-volatility scenarios using absolute
    volatility-point changes.

    Example:
        volatility = 20%
        -> [10%, 15%, 20%, 25%, 30%]
    """
    if volatility <= 0:
        raise ValueError("Volatility must be greater than zero.")
    if step <= 0 or min_change > max_change:
        raise ValueError("Invalid volatility scenario range or step.")

    # Keep the standard absolute-point shocks when all five are valid.
    offsets = []
    current = min_change
    while current <= max_change + 1e-9:
        offsets.append(round(current, 10))
        current += step

    candidate_scenarios = [volatility + offset for offset in offsets]
    if all(value > 0 for value in candidate_scenarios):
        return [round(value, 10) for value in candidate_scenarios]

    # For low base IV, use five distinct relative scenarios rather than
    # returning zero/negative volatility or failing the whole sensitivity call.
    factors = (0.50, 0.75, 1.00, 1.25, 1.50)
    return [round(volatility * factor, 10) for factor in factors]


def _position_multiplier(position: str) -> int:
    if position == "Long":
        return 1

    if position == "Short":
        return -1

    raise ValueError("Position must be 'Long' or 'Short'.")


def _calculate_metrics(
    option_type: str,
    spot: float,
    strike: float,
    volatility: float,
    rate: float,
    maturity: float,
    entry_price: float,
    quantity: float,
    position: str,
    dividend_yield: float,
) -> dict[str, float]:
    """
    Calculate price, Greeks and P&L for one scenario.
    """
    multiplier = _position_multiplier(position)

    price = option_price(
        option_type=option_type,
        spot=spot,
        strike=strike,
        volatility=volatility,
        rate=rate,
        maturity=maturity,
        dividend_yield=dividend_yield,
    )

    return {
        "delta": (
            delta(
                option_type=option_type,
                spot=spot,
                strike=strike,
                volatility=volatility,
                rate=rate,
                maturity=maturity,
                dividend_yield=dividend_yield,
            )
            * quantity
            * multiplier
        ),
        "gamma": (
            gamma(
                spot=spot,
                strike=strike,
                volatility=volatility,
                rate=rate,
                maturity=maturity,
                dividend_yield=dividend_yield,
            )
            * quantity
            * multiplier
        ),
        "theta": (
            theta(
                option_type=option_type,
                spot=spot,
                strike=strike,
                volatility=volatility,
                rate=rate,
                maturity=maturity,
                dividend_yield=dividend_yield,
            )
            * quantity
            * multiplier
        ),
        "vega": (
            vega(
                spot=spot,
                strike=strike,
                volatility=volatility,
                rate=rate,
                maturity=maturity,
                dividend_yield=dividend_yield,
            )
            * quantity
            * multiplier
        ),
        "pnl": (
            (price - entry_price)
            * quantity
            * multiplier
        ),
    }


def calculate_spot_sensitivity(
    option_type: str,
    spot: float,
    strike: float,
    volatility: float,
    rate: float,
    maturity: float,
    entry_price: float,
    quantity: float,
    position: str,
    dividend_yield: float = 0.0,
) -> dict:
    """
    Calculate trader-oriented sensitivity to spot movements.

    Volatility remains fixed at the base volatility.
    """
    variations = SPOT_VARIATIONS
    scenarios = generate_spot_scenarios(spot)

    metrics = [
        _calculate_metrics(
            option_type=option_type,
            spot=scenario_spot,
            strike=strike,
            volatility=volatility,
            rate=rate,
            maturity=maturity,
            entry_price=entry_price,
            quantity=quantity,
            position=position,
            dividend_yield=dividend_yield,
        )
        for scenario_spot in scenarios
    ]

    return {
        "variations": variations,
        "spots": scenarios,
        "delta": [item["delta"] for item in metrics],
        "gamma": [item["gamma"] for item in metrics],
        "theta": [item["theta"] for item in metrics],
        "vega": [item["vega"] for item in metrics],
        "pnl": [item["pnl"] for item in metrics],
    }


def calculate_volatility_sensitivity(
    option_type: str,
    spot: float,
    strike: float,
    volatility: float,
    rate: float,
    maturity: float,
    entry_price: float,
    quantity: float,
    position: str,
    dividend_yield: float = 0.0,
) -> dict:
    """
    Calculate trader-oriented sensitivity to implied-volatility movements.

    Spot remains fixed at the base spot price.
    """
    scenarios = generate_volatility_scenarios(volatility)
    # Labels are derived from the actual shocks, including the low-IV fallback.
    variations = [round(value - volatility, 10) for value in scenarios]

    metrics = [
        _calculate_metrics(
            option_type=option_type,
            spot=spot,
            strike=strike,
            volatility=scenario_volatility,
            rate=rate,
            maturity=maturity,
            entry_price=entry_price,
            quantity=quantity,
            position=position,
            dividend_yield=dividend_yield,
        )
        for scenario_volatility in scenarios
    ]

    return {
        "variations": variations,
        "volatilities": scenarios,
        "delta": [item["delta"] for item in metrics],
        "gamma": [item["gamma"] for item in metrics],
        "theta": [item["theta"] for item in metrics],
        "vega": [item["vega"] for item in metrics],
        "pnl": [item["pnl"] for item in metrics],
    }


def calculate_pnl_matrix(
    option_type: str,
    spot: float,
    strike: float,
    volatility: float,
    rate: float,
    maturity: float,
    entry_price: float,
    quantity: float,
    position: str,
    dividend_yield: float = 0.0,
) -> list[list[float]]:
    """
    Calculate the legacy combined spot/volatility P&L matrix.

    Kept for backwards compatibility with the existing API/tests.
    """
    spot_scenarios = generate_spot_scenarios(spot)
    volatility_scenarios = generate_volatility_scenarios(volatility)

    multiplier = _position_multiplier(position)

    matrix = []

    for scenario_spot in spot_scenarios:
        row = []

        for scenario_volatility in volatility_scenarios:
            scenario_price = option_price(
                option_type=option_type,
                spot=scenario_spot,
                strike=strike,
                volatility=scenario_volatility,
                rate=rate,
                maturity=maturity,
                dividend_yield=dividend_yield,
            )

            pnl = (
                scenario_price - entry_price
            ) * quantity * multiplier

            row.append(pnl)

        matrix.append(row)

    return matrix


def calculate_greek_matrix(
    greek: str,
    option_type: str,
    spot: float,
    strike: float,
    volatility: float,
    rate: float,
    maturity: float,
    quantity: float,
    position: str,
    dividend_yield: float = 0.0,
) -> list[list[float]]:
    """
    Calculate a Greek across combined spot/volatility scenarios.

    Kept for backwards compatibility with the existing API/tests.
    """
    spot_scenarios = generate_spot_scenarios(spot)
    volatility_scenarios = generate_volatility_scenarios(volatility)

    multiplier = _position_multiplier(position)

    matrix = []

    for scenario_spot in spot_scenarios:
        row = []

        for scenario_volatility in volatility_scenarios:
            if greek == "delta":
                value = delta(
                    option_type=option_type,
                    spot=scenario_spot,
                    strike=strike,
                    volatility=scenario_volatility,
                    rate=rate,
                    maturity=maturity,
                    dividend_yield=dividend_yield,
                )

            elif greek == "gamma":
                value = gamma(
                    spot=scenario_spot,
                    strike=strike,
                    volatility=scenario_volatility,
                    rate=rate,
                    maturity=maturity,
                    dividend_yield=dividend_yield,
                )

            elif greek == "theta":
                value = theta(
                    option_type=option_type,
                    spot=scenario_spot,
                    strike=strike,
                    volatility=scenario_volatility,
                    rate=rate,
                    maturity=maturity,
                    dividend_yield=dividend_yield,
                )

            elif greek == "vega":
                value = vega(
                    spot=scenario_spot,
                    strike=strike,
                    volatility=scenario_volatility,
                    rate=rate,
                    maturity=maturity,
                    dividend_yield=dividend_yield,
                )

            else:
                raise ValueError(f"Unsupported Greek: {greek}")

            row.append(value * quantity * multiplier)

        matrix.append(row)

    return matrix