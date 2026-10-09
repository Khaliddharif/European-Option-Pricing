from dataclasses import dataclass
from backend.app.models.position import Position
from backend.app.portfolio.calculator import PositionResult, calculate_position


@dataclass
class PortfolioResult:
    market_value: float
    pnl: float
    delta: float
    gamma: float
    theta: float
    vega: float
    initial_margin: float = 0.0
    maintenance_margin: float = 0.0


def calculate_portfolio(
    positions: list[Position], spot: float, rate: float, dividend_yield: float = 0.0,
) -> PortfolioResult:
    results: list[PositionResult] = [
        calculate_position(position, spot, rate, dividend_yield) for position in positions
    ]
    return PortfolioResult(
        market_value=sum(r.market_value for r in results),
        pnl=sum(r.pnl for r in results),
        delta=sum(r.delta for r in results),
        gamma=sum(r.gamma for r in results),
        theta=sum(r.theta for r in results),
        vega=sum(r.vega for r in results),
        initial_margin=sum(r.initial_margin for r in results),
        maintenance_margin=sum(r.maintenance_margin for r in results),
    )
