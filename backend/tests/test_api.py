from fastapi.testclient import TestClient

from backend.app.api.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_pricing_endpoint():
    response = client.post(
        "/pricing",
        json={
            "option_type": "Call",
            "spot": 100.0,
            "strike": 100.0,
            "volatility": 0.20,
            "rate": 0.05,
            "maturity": 1.0,
            "dividend_yield": 0.0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert abs(data["price"] - 10.45058357) < 1e-6
    assert abs(data["delta"] - 0.63683065) < 1e-6
    assert abs(data["gamma"] - 0.01876202) < 1e-6
    assert data["theta"] < 0
    assert data["vega"] > 0


def test_pricing_rejects_invalid_option_type():
    response = client.post(
        "/pricing",
        json={
            "option_type": "WrongType",
            "spot": 100.0,
            "strike": 100.0,
            "volatility": 0.20,
            "rate": 0.05,
            "maturity": 1.0,
            "dividend_yield": 0.0,
        },
    )

    assert response.status_code == 422


def test_pricing_rejects_negative_spot():
    response = client.post(
        "/pricing",
        json={
            "option_type": "Call",
            "spot": -100.0,
            "strike": 100.0,
            "volatility": 0.20,
            "rate": 0.05,
            "maturity": 1.0,
            "dividend_yield": 0.0,
        },
    )

    assert response.status_code == 422


def test_portfolio_endpoint():
    response = client.post(
        "/portfolio",
        json={
            "positions": [
                {
                    "asset": "Call",
                    "position": "Long",
                    "quantity": 100,
                    "entry_price": 5.0,
                    "maturity": 1.0,
                    "strike": 100.0,
                    "volatility": 0.20,
                },
                {
                    "asset": "Put",
                    "position": "Long",
                    "quantity": 50,
                    "entry_price": 4.0,
                    "maturity": 1.0,
                    "strike": 100.0,
                    "volatility": 0.20,
                },
            ],
            "spot": 100.0,
            "rate": 0.05,
            "dividend_yield": 0.0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert abs(data["market_value"] - 1323.734658331405) < 1e-5
    assert abs(data["pnl"] - 623.734658331405) < 1e-5
    assert data["delta"] > 0
    assert data["gamma"] > 0
    assert data["theta"] < 0
    assert data["vega"] > 0



def test_sensitivity_endpoint():
    response = client.post(
        "/sensitivity",
        json={
            "option_type": "Call",
            "position": "Long",
            "quantity": 100,
            "entry_price": 5.0,
            "spot": 100.0,
            "strike": 100.0,
            "volatility": 0.20,
            "rate": 0.05,
            "maturity": 1.0,
            "dividend_yield": 0.0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["spot_scenarios"]) == 9
    assert len(data["volatility_scenarios"]) == 5

    assert len(data["pnl_matrix"]) == 9
    assert len(data["delta_matrix"]) == 9
    assert len(data["gamma_matrix"]) == 9
    assert len(data["theta_matrix"]) == 9
    assert len(data["vega_matrix"]) == 9

    assert all(len(row) == 5 for row in data["pnl_matrix"])
    assert all(len(row) == 5 for row in data["delta_matrix"])
    assert all(len(row) == 5 for row in data["gamma_matrix"])
    assert all(len(row) == 5 for row in data["theta_matrix"])
    assert all(len(row) == 5 for row in data["vega_matrix"])