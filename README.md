# Option Pricing Tool

A Python-based option pricing and portfolio analytics application rebuilt from an original Excel/VBA implementation.

The project provides Black-Scholes option pricing, Greeks, implied volatility, portfolio analytics, and scenario-based sensitivity analysis through a REST API.

## Features

- European Call and Put pricing using the Black-Scholes model
- Option Greeks:
  - Delta
  - Gamma
  - Theta
  - Vega
- Implied volatility calculation
- Long and Short option positions
- Futures positions
- Portfolio-level:
  - Market value
  - P&L
  - Delta
  - Gamma
  - Theta
  - Vega
- Spot-price sensitivity analysis
- Volatility sensitivity analysis
- P&L and Greek sensitivity matrices
- Automated test suite with pytest
- REST API built with FastAPI

## Project Structure

```text
Option Pricing Tool/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── portfolio/
│   │   ├── pricing/
│   │   └── sensitivity/
│   │
│   └── tests/
│
├── frontend/
│
├── docs/
│
├── .gitignore
├── requirements.txt
└── README.md

Quantitative Models

The application uses the Black-Scholes-Merton framework for European options.

The implementation calculates:

Option price
Delta
Gamma
Theta
Vega
Rho
Implied volatility

The sensitivity engine evaluates option and portfolio behavior across changes in:

Underlying spot price
Implied volatility
API

The backend is implemented using FastAPI.

Available endpoints include:
GET  /health
POST /pricing
POST /implied-volatility
POST /portfolio
POST /sensitivity

Interactive API documentation is available through FastAPI's Swagger UI when the server is running:
http://127.0.0.1:8000/docs

Testing

The project uses pytest for automated testing.

Run the test suite with:

python -m pytest

Current test suite:

27 tests
27 passed


Technology Stack
Python
FastAPI
NumPy
SciPy
Pandas
Pytest
Uvicorn
Git / GitHub


Origin

This project is a Python reconstruction of an original Excel/VBA option pricing and portfolio analytics tool.

The original workbook contained:

European option pricing
Greeks
Implied volatility
Portfolio calculations
Spot/volatility sensitivity matrices
A VBA-based user interface

The Python implementation separates these components into a modular backend architecture suitable for testing, version control, and eventual web deployment.


Project Status

Completed
Black-Scholes pricing engine
Greeks
Implied volatility solver
Position model
Portfolio calculations
Sensitivity analysis
FastAPI backend
API validation
Automated testing
Project structure

Next
Web frontend
Interactive portfolio interface
Data visualization
GitHub repository
Deployment