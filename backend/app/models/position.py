from dataclasses import dataclass
from typing import Literal

AssetType = Literal["Call", "Put", "Future"]
PositionSide = Literal["Long", "Short"]
SettlementConvention = Literal["Cash", "Physical", "Daily mark-to-market", "Other"]


@dataclass
class Position:
    """Represents a single option or futures portfolio position."""

    asset: AssetType
    position: PositionSide
    quantity: float
    entry_price: float
    maturity: float | None = None
    strike: float | None = None
    volatility: float | None = None
    contract_multiplier: float = 1.0
    expiry_month: str | None = None
    currency: str = "EUR"
    tick_size: float | None = None
    tick_value: float | None = None
    initial_margin: float = 0.0
    maintenance_margin: float = 0.0
    settlement_convention: SettlementConvention = "Daily mark-to-market"

    def __post_init__(self) -> None:
        if self.asset not in {"Call", "Put", "Future"}:
            raise ValueError("Asset must be Call, Put, or Future.")
        if self.position not in {"Long", "Short"}:
            raise ValueError("Position must be Long or Short.")
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        if self.entry_price < 0:
            raise ValueError("Entry price cannot be negative.")
        if self.contract_multiplier <= 0:
            raise ValueError("Contract multiplier must be greater than zero.")
        if not self.currency or len(self.currency.strip()) != 3:
            raise ValueError("Currency must be a three-letter code, such as EUR.")
        if self.tick_size is not None and self.tick_size <= 0:
            raise ValueError("Tick size must be greater than zero when provided.")
        if self.tick_value is not None and self.tick_value <= 0:
            raise ValueError("Tick value must be greater than zero when provided.")
        if self.initial_margin < 0 or self.maintenance_margin < 0:
            raise ValueError("Margin amounts cannot be negative.")
        if self.maintenance_margin > self.initial_margin and self.initial_margin > 0:
            raise ValueError("Maintenance margin cannot exceed initial margin.")
        if self.asset in {"Call", "Put"}:
            if self.maturity is None:
                raise ValueError("Maturity is required for options.")
            if self.strike is None:
                raise ValueError("Strike is required for options.")
            if self.volatility is None:
                raise ValueError("Volatility is required for options.")
            if self.maturity <= 0:
                raise ValueError("Maturity must be greater than zero.")
            if self.strike <= 0:
                raise ValueError("Strike must be greater than zero.")
            if self.volatility <= 0:
                raise ValueError("Volatility must be greater than zero.")
