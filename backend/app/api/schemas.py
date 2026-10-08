from pydantic import BaseModel, Field


class PricingRequest(BaseModel):
    option_type: str = Field(pattern="^(Call|Put)$")
    spot: float = Field(gt=0)
    strike: float = Field(gt=0)
    volatility: float = Field(gt=0)
    rate: float
    maturity: float = Field(gt=0)
    dividend_yield: float = 0.0


class PricingResponse(BaseModel):
    price: float
    delta: float
    gamma: float
    theta: float
    vega: float


class ImpliedVolatilityRequest(BaseModel):
    option_type: str = Field(pattern="^(Call|Put)$")
    spot: float = Field(gt=0)
    strike: float = Field(gt=0)
    rate: float
    maturity: float = Field(gt=0)
    dividend_yield: float = 0.0
    option_value: float = Field(gt=0)


class ImpliedVolatilityResponse(BaseModel):
    implied_volatility: float


class PositionRequest(BaseModel):
    asset: str = Field(pattern="^(Call|Put|Future)$")
    position: str = Field(pattern="^(Long|Short)$")
    quantity: float = Field(gt=0)
    entry_price: float = Field(ge=0)
    maturity: float | None = Field(default=None, gt=0)
    strike: float | None = Field(default=None, gt=0)
    volatility: float | None = Field(default=None, gt=0)


class PortfolioRequest(BaseModel):
    positions: list[PositionRequest]
    spot: float = Field(gt=0)
    rate: float
    dividend_yield: float = 0.0


class PortfolioResponse(BaseModel):
    market_value: float
    pnl: float
    delta: float
    gamma: float
    theta: float
    vega: float


class SensitivityRequest(BaseModel):
    option_type: str = Field(pattern="^(Call|Put)$")
    position: str = Field(pattern="^(Long|Short)$")
    quantity: float = Field(gt=0)
    entry_price: float = Field(ge=0)
    spot: float = Field(gt=0)
    strike: float = Field(gt=0)
    volatility: float = Field(gt=0)
    rate: float
    maturity: float = Field(gt=0)
    dividend_yield: float = 0.0


class SensitivityResponse(BaseModel):
    spot_scenarios: list[float]
    volatility_scenarios: list[float]
    pnl_matrix: list[list[float]]
    delta_matrix: list[list[float]]
    gamma_matrix: list[list[float]]
    theta_matrix: list[list[float]]
    vega_matrix: list[list[float]]