from dataclasses import dataclass

from backend.app.models.position import Position
from backend.app.pricing.black_scholes import option_price, delta, gamma, theta, vega


@dataclass
class PositionResult:
    """Calculated risk metrics for a single position."""
    market_value: float
    pnl: float
    delta: float
    gamma: float
    theta: float
    vega: float
    initial_margin: float = 0.0
    maintenance_margin: float = 0.0


def calculate_position(
    position: Position,
    spot: float,
    rate: float,
    dividend_yield: float = 0.0,
) -> PositionResult:
    """Calculate current value, P&L, Greeks, and supplied margin estimates."""
    if position.asset == "Future":
        return _calculate_future(position=position, spot=spot)

    price = option_price(
        option_type=position.asset, spot=spot, strike=position.strike,
        volatility=position.volatility, rate=rate, maturity=position.maturity,
        dividend_yield=dividend_yield,
    )
    option_delta = delta(
        option_type=position.asset, spot=spot, strike=position.strike,
        volatility=position.volatility, rate=rate, maturity=position.maturity,
        dividend_yield=dividend_yield,
    )
    option_gamma = gamma(
        spot=spot, strike=position.strike, volatility=position.volatility,
        rate=rate, maturity=position.maturity, dividend_yield=dividend_yield,
    )
    option_theta = theta(
        option_type=position.asset, spot=spot, strike=position.strike,
        volatility=position.volatility, rate=rate, maturity=position.maturity,
        dividend_yield=dividend_yield,
    )
    option_vega = vega(
        spot=spot, strike=position.strike, volatility=position.volatility,
        rate=rate, maturity=position.maturity, dividend_yield=dividend_yield,
    )
    side = 1 if position.position == "Long" else -1
    scale = position.quantity * side
    # Preserve the existing option unit convention; the new multiplier is
    # applied to futures only in this version.
    return PositionResult(
        market_value=price * scale,
        pnl=(price - position.entry_price) * scale,
        delta=option_delta * scale,
        gamma=option_gamma * scale,
        theta=option_theta * scale,
        vega=option_vega * scale,
        initial_margin=position.initial_margin * position.quantity,
        maintenance_margin=position.maintenance_margin * position.quantity,
    )


def _calculate_future(position: Position, spot: float) -> PositionResult:
    """Linear futures P&L. Margin inputs are per-contract estimates supplied by the user."""
    side = 1 if position.position == "Long" else -1
    contracts_scale = position.quantity * position.contract_multiplier * side
    return PositionResult(
        market_value=spot * contracts_scale,
        pnl=(spot - position.entry_price) * contracts_scale,
        delta=contracts_scale,
        gamma=0.0,
        theta=0.0,
        vega=0.0,
        initial_margin=position.initial_margin * position.quantity,
        maintenance_margin=position.maintenance_margin * position.quantity,
    )
