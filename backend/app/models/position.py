from dataclasses import dataclass
from typing import Literal


AssetType = Literal["Call", "Put", "Future"]
PositionSide = Literal["Long", "Short"]


@dataclass
class Position:
    """
    Represents a single portfolio position.
    """

    asset: AssetType
    position: PositionSide
    quantity: float
    entry_price: float
    maturity: float | None = None
    strike: float | None = None
    volatility: float | None = None

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        if self.entry_price < 0:
            raise ValueError("Entry price cannot be negative.")

        if self.asset in {"Call", "Put"}:
            if self.maturity is None:
                raise ValueError(
                    "Maturity is required for options."
                )

            if self.strike is None:
                raise ValueError(
                    "Strike is required for options."
                )

            if self.volatility is None:
                raise ValueError(
                    "Volatility is required for options."
                )

            if self.maturity <= 0:
                raise ValueError(
                    "Maturity must be greater than zero."
                )

            if self.strike <= 0:
                raise ValueError(
                    "Strike must be greater than zero."
                )

            if self.volatility <= 0:
                raise ValueError(
                    "Volatility must be greater than zero."
                )