from fastapi import FastAPI

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
)


app = FastAPI(
    title="Option Pricing Tool API",
    version="1.0.0",
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
    )


@app.post(
    "/sensitivity",
    response_model=SensitivityResponse,
)
def calculate_sensitivity(
    request: SensitivityRequest,
) -> SensitivityResponse:
    spot_scenarios = generate_spot_scenarios(
        request.spot
    )

    volatility_scenarios = generate_volatility_scenarios(
        request.volatility
    )

    pnl_matrix = calculate_pnl_matrix(
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

    delta_matrix = calculate_greek_matrix(
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
    )

    gamma_matrix = calculate_greek_matrix(
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
    )

    theta_matrix = calculate_greek_matrix(
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
    )

    vega_matrix = calculate_greek_matrix(
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
    )

    return SensitivityResponse(
        spot_scenarios=spot_scenarios,
        volatility_scenarios=volatility_scenarios,
        pnl_matrix=pnl_matrix,
        delta_matrix=delta_matrix,
        gamma_matrix=gamma_matrix,
        theta_matrix=theta_matrix,
        vega_matrix=vega_matrix,
    )