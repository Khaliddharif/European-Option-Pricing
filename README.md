# European Option Pricing - Risk & Portfolio Analytics

A Python and React application for European option pricing, option
Greeks, implied volatility, sensitivity analysis, and portfolio-level
risk analytics. The application was rebuilt from an original Excel/VBA
implementation.

> **Market data:** Live market-data integration is not currently
> included. Prices are entered manually. Live market data is a planned
> feature, subject to provider permissions and licensing.

## Features

-   European Call and Put pricing using the Black--Scholes framework.
-   Option Greeks: Delta, Gamma, Theta, Vega, and Rho where exposed by
    the pricing implementation.
-   Implied-volatility calculation with input and no-arbitrage-bound
    validation.
-   Long and Short option positions.
-   Futures positions with a user-entered contract multiplier.
-   Futures contract metadata: expiry/delivery month, currency, tick
    size, tick value, initial and maintenance margin, and settlement
    convention.
-   Position and portfolio calculations: signed market value, P&L,
    Delta, Gamma, Theta, and Vega.
-   Estimated initial and maintenance margin totals based on manually
    entered per-contract values.
-   Spot-price and implied-volatility scenario analysis.
-   P&L and Greek sensitivity matrices.
-   Trade journal with trade deletion and CSV export.
-   Metric help tooltips and keyboard-oriented trade entry.
-   FastAPI REST API and interactive Swagger documentation.
-   Automated backend tests with pytest.

## Project structure

``` text
Option Pricing Tool/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── main.py
│   │   │   └── schemas.py
│   │   ├── models/
│   │   │   └── position.py
│   │   ├── portfolio/
│   │   │   ├── calculator.py
│   │   │   └── portfolio.py
│   │   ├── pricing/
│   │   │   ├── black_scholes.py
│   │   │   └── implied_volatility.py
│   │   └── sensitivity/
│   │       └── calculator.py
│   └── tests/
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       ├── index.css
│       └── main.jsx
├── requirements.txt
└── README.md
```

## Requirements

-   Python (the project has been tested in the developer environment
    with Python 3.14.2).
-   Node.js and npm (tested in the developer environment with Node.js
    24.13.0 and npm 11.8.0).
-   A modern browser.

Install the Python dependencies from the project root:

``` powershell
python -m pip install -r requirements.txt
```

Install the frontend dependencies:

``` powershell
cd frontend
npm install
```

## Run the application locally

Open two terminals.

### Terminal 1: backend

From the project root:

``` powershell
python -m uvicorn backend.app.api.main:app --reload
```

Backend health check:

``` text
http://127.0.0.1:8000/health
```

Interactive API documentation:

``` text
http://127.0.0.1:8000/docs
```

### Terminal 2: frontend

From the project root:

``` powershell
cd frontend
npm run dev
```

Open the local URL printed by Vite. If Vite uses a port other than 5173,
ensure that port is allowed by the backend CORS configuration in
`backend/app/api/main.py`.

### Production frontend build

From `frontend/`:

``` powershell
npm run build
```

## API endpoints

  -----------------------------------------------------------------------
  Method                  Endpoint                Purpose
  ----------------------- ----------------------- -----------------------
  `GET`                   `/health`               Returns API health
                                                  status.

  `POST`                  `/pricing`              Calculates an option's
                                                  theoretical price and
                                                  exposed pricing
                                                  metrics.

  `POST`                  `/implied-volatility`   Solves for implied
                                                  volatility from an
                                                  option value.

  `POST`                  `/portfolio`            Calculates aggregate
                                                  portfolio market value,
                                                  P&L, and Greeks,
                                                  including supported
                                                  futures position
                                                  fields.

  `POST`                  `/sensitivity`          Returns spot and
                                                  volatility sensitivity
                                                  results and the legacy
                                                  scenario matrices.
  -----------------------------------------------------------------------

The exact request and response fields are defined in
`backend/app/api/schemas.py`. Open `/docs` while the backend is running
to inspect the current API schema and try requests.

## Function and module reference

This section inventories the main functions and callable components used
by the application. The implementation in the source files is
authoritative if a signature or behavior changes.

### API: `backend/app/api/main.py`

-   `health_check()` --- returns a simple status payload for health
    checks.
-   `calculate_pricing(request)` --- handles `/pricing` and returns the
    option model outputs exposed by `PricingResponse`.
-   `calculate_implied_volatility(request)` --- handles
    `/implied-volatility` and returns the solved implied volatility.
-   `calculate_portfolio_api(request)` --- converts API position
    requests into `Position` objects, calculates portfolio results, and
    serializes the response.
-   `sensitivity(request)` --- handles `/sensitivity`, returning
    trader-oriented spot and volatility sensitivity plus compatibility
    matrices.

### API schemas: `backend/app/api/schemas.py`

These Pydantic model classes validate incoming requests and shape
outgoing responses:

-   `PricingRequest` / `PricingResponse` --- option pricing request and
    result.
-   `ImpliedVolatilityRequest` / `ImpliedVolatilityResponse` ---
    implied-volatility inputs and result.
-   `PositionRequest` --- one portfolio position, including option
    fields and supported futures contract metadata.
-   `PortfolioRequest` / `PortfolioResponse` --- portfolio inputs and
    aggregate outputs.
-   `SensitivityRequest` / `SensitivityResponse` --- sensitivity inputs,
    scenario labels, and matrix outputs.

### Position model: `backend/app/models/position.py`

-   `Position` --- dataclass representing a Call, Put, or Future
    position.
-   `Position.__post_init__()` --- validates quantity, entry price, and
    required positive option maturity, strike, and volatility.

### Option pricing: `backend/app/pricing/black_scholes.py`

The pricing module provides the Black--Scholes calculations used by the
API, portfolio calculator, and sensitivity engine:

-   `option_price(...)` --- theoretical European Call or Put price.
-   `delta(...)` --- first-order sensitivity to the underlying price.
-   `gamma(...)` --- sensitivity of Delta to the underlying price.
-   `theta(...)` --- model time-decay measure.
-   `vega(...)` --- sensitivity to volatility.
-   `rho(...)` --- sensitivity to the risk-free rate, if included in the
    current module/API version.

The source file defines the authoritative signatures and parameter
defaults.

### Implied volatility: `backend/app/pricing/implied_volatility.py`

-   `implied_volatility(...)` --- solves for volatility consistent with
    an observed option value and model inputs; validates inputs and
    option-price bounds.

### Position and portfolio calculations

`backend/app/portfolio/calculator.py`:

-   `PositionResult` --- dataclass containing position-level market
    value, P&L, and Greeks.
-   `calculate_position(position, spot, rate, dividend_yield=0.0)` ---
    calculates one position's value, P&L, and risk metrics.
-   `_calculate_future(position, spot)` --- internal helper for the
    simplified linear futures calculation. Futures use the contract
    multiplier where configured; option-only Greeks are zero for this
    simplified model.

`backend/app/portfolio/portfolio.py`:

-   `PortfolioResult` --- dataclass containing aggregate market value,
    P&L, and Greeks.
-   `calculate_portfolio(positions, spot, rate, dividend_yield=0.0)` ---
    calculates each position and sums its results.

### Sensitivity engine: `backend/app/sensitivity/calculator.py`

-   `generate_spot_scenarios(spot)` --- creates spot-price scenarios
    around the base spot.
-   `generate_volatility_scenarios(volatility)` --- creates positive
    volatility scenarios around the base volatility.
-   `calculate_pnl_matrix(...)` --- computes P&L across spot and
    volatility scenario combinations.
-   `calculate_greek_matrix(...)` --- computes a selected Greek across
    scenario combinations.
-   `calculate_spot_sensitivity(...)` --- produces trader-oriented
    metrics for spot-price changes.
-   `calculate_volatility_sensitivity(...)` --- produces trader-oriented
    metrics for volatility changes.

### Frontend: `frontend/src/App.jsx`

The React frontend includes the following main helpers and components
(names may differ if the frontend is refactored):

-   `fmt(value, decimals)` --- formats finite numeric values for
    display.
-   `money(value)` --- formats monetary values.
-   `percent(value)` --- formats decimal values as percentages.
-   `errorText(error)` --- converts thrown errors into displayable
    messages.
-   `tradePnl(trade)` --- calculates displayed trade P&L from current
    model value or futures price, entry price, quantity, and direction.
-   `Metric` --- displays a metric label, value, optional hint, and help
    explanation.
-   `scenarioLabels(scenarios, base, type)` --- converts absolute
    scenario values into relative percentage labels.
-   `SensitivityTable` --- renders the sensitivity metrics table.
-   `DeleteConfirmation` --- renders the trade deletion confirmation
    dialog.
-   `App` --- owns the trade form, requests to the API, session trade
    journal, portfolio summary, sensitivity results, and CSV export.
-   `requestJson(path, body)` --- posts JSON to the backend and handles
    unsuccessful responses.
-   `makePortfolioPayload(tradeList)` --- builds the portfolio API
    payload from session trades.
-   `handleCompute(event)` --- validates form inputs, calls
    pricing/sensitivity endpoints where applicable, adds the trade, and
    refreshes portfolio analytics.
-   `handleConfirmDelete()` --- removes a selected trade and refreshes
    the portfolio summary.

The frontend's exact function list should be checked against the final
`App.jsx` before release, especially if helper functions were renamed
during the recent UI updates.

## Quantitative model notes and limitations

-   European option pricing uses the Black--Scholes framework and
    depends on the entered spot, strike, volatility, risk-free rate,
    time to maturity, and dividend yield.
-   Prices are manually entered; the application does not currently
    fetch live market quotes.
-   Portfolio P&L is model-based and compares current model value
    (options) or current futures price (futures) with the entered entry
    price.
-   Futures calculations are simplified and linear. The multiplier
    scales exposure and P&L. The market value shown is signed notional
    exposure, not necessarily the cash paid to open a futures position.
-   Initial and maintenance margin are estimates calculated from
    user-entered per-contract amounts. They are not live exchange or
    broker margin requirements.
-   The app records contract expiry/delivery month, currency, tick
    details, and settlement convention; it does not model the complete
    delivery process, daily variation-margin cash flows, fees, or all
    broker-specific settlement rules.
-   Greeks are model sensitivities, not guarantees of future P&L. Actual
    outcomes can differ due to market movements, volatility changes,
    transaction costs, liquidity, and model assumptions.
-   The current trade journal is session-based. Do not assume trades
    persist after a browser refresh unless persistence has been
    implemented separately.

## Testing

Run all backend tests from the project root:

``` powershell
python -m pytest backend/tests -q
```

The last reported backend test run in the development conversation was
**47 passed**. Re-run the command against the version you intend to
publish.

Build the frontend from `frontend/`:

``` powershell
npm run build
```

The last reported production build completed successfully with Vite.
Re-run it after any final source changes.

## Technology stack

-   Python
-   FastAPI
-   Pydantic
-   NumPy / SciPy (as used by the quantitative modules)
-   pytest
-   Uvicorn
-   React
-   Vite
-   JavaScript / CSS
-   Git and GitHub

## Project origin

This project is a Python/React reconstruction of an original Excel/VBA
option-pricing and portfolio-analytics workbook. The code separates
pricing, position modelling, portfolio aggregation, sensitivity
analysis, and API concerns into testable modules.

## Roadmap

-   Complete final manual regression checks and documentation.
-   Publish a clean repository and demonstration screenshots.
-   Consider visualization and deployment improvements.
-   Investigate live market-data integration only after confirming the
    applicable provider permissions, licensing, and redistribution
    terms.

## Developer

It's me Khalid Dharif: Hello world! :D

-   Email: <khalid.dharif@gmail.com>
-   GitHub: [github.com/Khaliddharif](https://github.com/Khaliddharif)
