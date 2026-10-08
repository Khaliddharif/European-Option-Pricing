from backend.app.pricing.black_scholes import (
    option_price,
    delta,
    gamma,
    theta,
    vega,
)





def generate_spot_scenarios(
    spot: float,
    min_change: float = -0.20,
    max_change: float = 0.20,
    step: float = 0.05,
) -> list[float]:
    changes = []

    current = min_change

    while current <= max_change + 1e-9:
        changes.append(round(spot * (1 + current), 10))
        current += step

    return changes


def generate_volatility_scenarios(
    volatility: float,
    min_change: float = -0.10,
    max_change: float = 0.10,
    step: float = 0.05,
) -> list[float]:
    changes = []

    current = min_change

    while current <= max_change + 1e-9:
        changes.append(round(volatility * (1 + current), 10))
        current += step

    return changes






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
    spot_scenarios = generate_spot_scenarios(spot)
    volatility_scenarios = generate_volatility_scenarios(volatility)

    side_multiplier = 1 if position == "Long" else -1

    matrix = []

    for scenario_spot in spot_scenarios:
        row = []

        for scenario_volatility in volatility_scenarios:
            price = option_price(
                option_type=option_type,
                spot=scenario_spot,
                strike=strike,
                volatility=scenario_volatility,
                rate=rate,
                maturity=maturity,
                dividend_yield=dividend_yield,
            )

            pnl = (
                (price - entry_price)
                * quantity
                * side_multiplier
            )

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
    spot_scenarios = generate_spot_scenarios(spot)
    volatility_scenarios = generate_volatility_scenarios(volatility)

    side_multiplier = 1 if position == "Long" else -1

    if greek.lower() not in {"delta", "gamma", "theta", "vega"}:
        raise ValueError(
            "Greek must be one of: delta, gamma, theta, vega"
        )

    matrix = []

    for scenario_spot in spot_scenarios:
        row = []

        for scenario_volatility in volatility_scenarios:
            if greek.lower() == "delta":
                value = delta(
                    option_type=option_type,
                    spot=scenario_spot,
                    strike=strike,
                    volatility=scenario_volatility,
                    rate=rate,
                    maturity=maturity,
                    dividend_yield=dividend_yield,
                )

            elif greek.lower() == "gamma":
                value = gamma(
                    spot=scenario_spot,
                    strike=strike,
                    volatility=scenario_volatility,
                    rate=rate,
                    maturity=maturity,
                    dividend_yield=dividend_yield,
                )

            elif greek.lower() == "theta":
                value = theta(
                    option_type=option_type,
                    spot=scenario_spot,
                    strike=strike,
                    volatility=scenario_volatility,
                    rate=rate,
                    maturity=maturity,
                    dividend_yield=dividend_yield,
                )

            else:
                value = vega(
                    spot=scenario_spot,
                    strike=strike,
                    volatility=scenario_volatility,
                    rate=rate,
                    maturity=maturity,
                    dividend_yield=dividend_yield,
                )

            value *= quantity * side_multiplier
            row.append(value)

        matrix.append(row)

    return matrix