from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.schemas import (
    PricingRequest,
    PricingResponse,
    ImpliedVolatilityRequest,
    ImpliedVolatilityResponse,
    PositionRequest,
    PortfolioRequest,
    PortfolioResponse,
    SensitivityRequest,
    SensitivityResponse,
)

from backend.app.models.position import Position

from backend.app.pricing.black_scholes import (
    option_price,
    delta,
    gamma,
    theta,
    vega,
)

from backend.app.pricing.implied_volatility import implied_volatility

from backend.app.portfolio.portfolio import calculate_portfolio

from backend.app.sensitivity.calculator import (
    generate_spot_scenarios,
    generate_volatility_scenarios,
    calculate_pnl_matrix,
    calculate_greek_matrix,
    calculate_spot_sensitivity,
    calculate_volatility_sensitivity,
)


app = FastAPI(
    title="Option Pricing Tool API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "https://european-option-pricing.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/pricing", response_model=PricingResponse)
def calculate_pricing(
    request: PricingRequest,
) -> PricingResponse:
    return PricingResponse(
        price=option_price(
            option_type=request.option_type,
            spot=request.spot,
            strike=request.strike,
            volatility=request.volatility,
            rate=request.rate,
            maturity=request.maturity,
            dividend_yield=request.dividend_yield,
        ),
        delta=delta(
            option_type=request.option_type,
            spot=request.spot,
            strike=request.strike,
            volatility=request.volatility,
            rate=request.rate,
            maturity=request.maturity,
            dividend_yield=request.dividend_yield,
        ),
        gamma=gamma(
            spot=request.spot,
            strike=request.strike,
            volatility=request.volatility,
            rate=request.rate,
            maturity=request.maturity,
            dividend_yield=request.dividend_yield,
        ),
        theta=theta(
            option_type=request.option_type,
            spot=request.spot,
            strike=request.strike,
            volatility=request.volatility,
            rate=request.rate,
            maturity=request.maturity,
            dividend_yield=request.dividend_yield,
        ),
        vega=vega(
            spot=request.spot,
            strike=request.strike,
            volatility=request.volatility,
            rate=request.rate,
            maturity=request.maturity,
            dividend_yield=request.dividend_yield,
        ),
    )


@app.post(
    "/implied-volatility",
    response_model=ImpliedVolatilityResponse,
)
def calculate_implied_volatility(
    request: ImpliedVolatilityRequest,
) -> ImpliedVolatilityResponse:
    result = implied_volatility(
        option_type=request.option_type,
        spot=request.spot,
        strike=request.strike,
        rate=request.rate,
        maturity=request.maturity,
        dividend_yield=request.dividend_yield,
        option_value=request.option_value,
    )

    return ImpliedVolatilityResponse(
        implied_volatility=result,
    )


@app.post(
    "/portfolio",
    response_model=PortfolioResponse,
)
def calculate_portfolio_api(
    request: PortfolioRequest,
) -> PortfolioResponse:
    positions = [
        Position(
            asset=position.asset,
            position=position.position,
            quantity=position.quantity,
            entry_price=position.entry_price,
            maturity=position.maturity,
            strike=position.strike,
            volatility=position.volatility,
            contract_multiplier=position.contract_multiplier,
            expiry_month=position.expiry_month,
            currency=position.currency.upper(),
            tick_size=position.tick_size,
            tick_value=position.tick_value,
            initial_margin=position.initial_margin,
            maintenance_margin=position.maintenance_margin,
            settlement_convention=position.settlement_convention,
        )
        for position in request.positions
    ]

    result = calculate_portfolio(
        positions=positions,
        spot=request.spot,
        rate=request.rate,
        dividend_yield=request.dividend_yield,
    )

    return PortfolioResponse(
        market_value=result.market_value,
        pnl=result.pnl,
        delta=result.delta,
        gamma=result.gamma,
        theta=result.theta,
        vega=result.vega,
        initial_margin=result.initial_margin,
        maintenance_margin=result.maintenance_margin,
    )


@app.post(
    "/sensitivity",
    response_model=SensitivityResponse,
)
def sensitivity(
    request: SensitivityRequest,
) -> SensitivityResponse:
    """
    Calculate trader-oriented spot and implied-volatility
    sensitivity analysis.

    The endpoint also returns the legacy combined matrices
    so existing API consumers and tests remain compatible.
    """

    spot_sensitivity = calculate_spot_sensitivity(
        option_type=request.option_type,
        spot=request.spot,
        strike=request.strike,
        volatility=request.volatility,
        rate=request.rate,
        maturity=request.maturity,
        entry_price=request.entry_price,
        quantity=request.quantity,
        position=request.position,
        dividend_yield=request.dividend_yield,
    )

    volatility_sensitivity = calculate_volatility_sensitivity(
        option_type=request.option_type,
        spot=request.spot,
        strike=request.strike,
        volatility=request.volatility,
        rate=request.rate,
        maturity=request.maturity,
        entry_price=request.entry_price,
        quantity=request.quantity,
        position=request.position,
        dividend_yield=request.dividend_yield,
    )

    return SensitivityResponse(
        # New trader-oriented sensitivity results
        spot_sensitivity=spot_sensitivity,
        volatility_sensitivity=volatility_sensitivity,

        # Existing combined sensitivity results
        spot_scenarios=generate_spot_scenarios(
            request.spot
        ),
        volatility_scenarios=generate_volatility_scenarios(
            request.volatility
        ),

        pnl_matrix=calculate_pnl_matrix(
            option_type=request.option_type,
            spot=request.spot,
            strike=request.strike,
            volatility=request.volatility,
            rate=request.rate,
            maturity=request.maturity,
            entry_price=request.entry_price,
            quantity=request.quantity,
            position=request.position,
            dividend_yield=request.dividend_yield,
        ),

        delta_matrix=calculate_greek_matrix(
            greek="delta",
            option_type=request.option_type,
            spot=request.spot,
            strike=request.strike,
            volatility=request.volatility,
            rate=request.rate,
            maturity=request.maturity,
            quantity=request.quantity,
            position=request.position,
            dividend_yield=request.dividend_yield,
        ),

        gamma_matrix=calculate_greek_matrix(
            greek="gamma",
            option_type=request.option_type,
            spot=request.spot,
            strike=request.strike,
            volatility=request.volatility,
            rate=request.rate,
            maturity=request.maturity,
            quantity=request.quantity,
            position=request.position,
            dividend_yield=request.dividend_yield,
        ),

        theta_matrix=calculate_greek_matrix(
            greek="theta",
            option_type=request.option_type,
            spot=request.spot,
            strike=request.strike,
            volatility=request.volatility,
            rate=request.rate,
            maturity=request.maturity,
            quantity=request.quantity,
            position=request.position,
            dividend_yield=request.dividend_yield,
        ),

        vega_matrix=calculate_greek_matrix(
            greek="vega",
            option_type=request.option_type,
            spot=request.spot,
            strike=request.strike,
            volatility=request.volatility,
            rate=request.rate,
            maturity=request.maturity,
            quantity=request.quantity,
            position=request.position,
            dividend_yield=request.dividend_yield,
        ),
    )