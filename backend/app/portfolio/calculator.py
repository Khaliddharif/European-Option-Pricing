from dataclasses import dataclass

from backend.app.models.position import Position
from backend.app.pricing.black_scholes import (
    option_price,
    delta,
    gamma,
    theta,
    vega,
)


@dataclass
class PositionResult:
    """
    Calculated risk metrics for a single position.
    """

    market_value: float
    pnl: float
    delta: float
    gamma: float
    theta: float
    vega: float


def calculate_position(
    position: Position,
    spot: float,
    rate: float,
    dividend_yield: float = 0.0,
) -> PositionResult:
    """
    Calculate the current value, P&L and Greeks for a position.
    """

    if position.asset == "Future":
        return _calculate_future(
            position=position,
            spot=spot,
        )

    price = option_price(
        option_type=position.asset,
        spot=spot,
        strike=position.strike,
        volatility=position.volatility,
        rate=rate,
        maturity=position.maturity,
        dividend_yield=dividend_yield,
    )

    option_delta = delta(
        option_type=position.asset,
        spot=spot,
        strike=position.strike,
        volatility=position.volatility,
        rate=rate,
        maturity=position.maturity,
        dividend_yield=dividend_yield,
    )

    option_gamma = gamma(
        spot=spot,
        strike=position.strike,
        volatility=position.volatility,
        rate=rate,
        maturity=position.maturity,
        dividend_yield=dividend_yield,
    )

    option_theta = theta(
        option_type=position.asset,
        spot=spot,
        strike=position.strike,
        volatility=position.volatility,
        rate=rate,
        maturity=position.maturity,
        dividend_yield=dividend_yield,
    )

    option_vega = vega(
        spot=spot,
        strike=position.strike,
        volatility=position.volatility,
        rate=rate,
        maturity=position.maturity,
        dividend_yield=dividend_yield,
    )

    side_multiplier = 1 if position.position == "Long" else -1

    market_value = (
        price
        * position.quantity
        * side_multiplier
    )

    pnl = (
        (price - position.entry_price)
        * position.quantity
        * side_multiplier
    )

    return PositionResult(
        market_value=market_value,
        pnl=pnl,
        delta=option_delta * position.quantity * side_multiplier,
        gamma=option_gamma * position.quantity * side_multiplier,
        theta=option_theta * position.quantity * side_multiplier,
        vega=option_vega * position.quantity * side_multiplier,
    )


def _calculate_future(
    position: Position,
    spot: float,
) -> PositionResult:
    """
    Calculate P&L for a futures position.

    Futures do not have Black-Scholes option Greeks.
    """

    side_multiplier = 1 if position.position == "Long" else -1

    market_value = (
        spot
        * position.quantity
        * side_multiplier
    )

    pnl = (
        (spot - position.entry_price)
        * position.quantity
        * side_multiplier
    )

    return PositionResult(
        market_value=market_value,
        pnl=pnl,
        delta=position.quantity * side_multiplier,
        gamma=0.0,
        theta=0.0,
        vega=0.0,
    )