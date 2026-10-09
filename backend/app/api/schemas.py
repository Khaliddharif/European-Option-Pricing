from pydantic import BaseModel, Field, model_validator


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
    contract_multiplier: float = Field(default=1.0, gt=0)
    expiry_month: str | None = Field(default=None, max_length=32)
    currency: str = Field(default="EUR", min_length=3, max_length=3, pattern="^[A-Za-z]{3}$")
    tick_size: float | None = Field(default=None, gt=0)
    tick_value: float | None = Field(default=None, gt=0)
    initial_margin: float = Field(default=0.0, ge=0)
    maintenance_margin: float = Field(default=0.0, ge=0)
    settlement_convention: str = Field(default="Daily mark-to-market", pattern="^(Cash|Physical|Daily mark-to-market|Other)$")

    @model_validator(mode="after")
    def validate_margin_relationship(self):
        if self.initial_margin > 0 and self.maintenance_margin > self.initial_margin:
            raise ValueError("Maintenance margin cannot exceed initial margin.")
        return self


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
    initial_margin: float = 0.0
    maintenance_margin: float = 0.0


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
    spot_sensitivity: dict
    volatility_sensitivity: dict

    # Legacy combined matrices retained for compatibility.
    spot_scenarios: list[float]
    volatility_scenarios: list[float]
    pnl_matrix: list[list[float]]
    delta_matrix: list[list[float]]
    gamma_matrix: list[list[float]]
    theta_matrix: list[list[float]]
    vega_matrix: list[list[float]]