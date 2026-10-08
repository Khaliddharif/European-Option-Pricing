from dataclasses import dataclass

from backend.app.models.position import Position
from backend.app.portfolio.calculator import (
    PositionResult,
    calculate_position,
)


@dataclass
class PortfolioResult:
    market_value: float
    pnl: float
    delta: float
    gamma: float
    theta: float
    vega: float


def calculate_portfolio(
    positions: list[Position],
    spot: float,
    rate: float,
    dividend_yield: float = 0.0,
) -> PortfolioResult:
    results: list[PositionResult] = [
        calculate_position(
            position=position,
            spot=spot,
            rate=rate,
            dividend_yield=dividend_yield,
        )
        for position in positions
    ]

    return PortfolioResult(
        market_value=sum(result.market_value for result in results),
        pnl=sum(result.pnl for result in results),
        delta=sum(result.delta for result in results),
        gamma=sum(result.gamma for result in results),
        theta=sum(result.theta for result in results),
        vega=sum(result.vega for result in results),
    )