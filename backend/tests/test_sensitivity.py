from backend.app.sensitivity.calculator import (
    generate_spot_scenarios,
    generate_volatility_scenarios,
    calculate_pnl_matrix,
    calculate_greek_matrix,
)


def test_generate_spot_scenarios():
    scenarios = generate_spot_scenarios(100.0)

    assert scenarios == [
        80.0,
        90.0,
        100.0,
        110.0,
        120.0,
    ]


def test_generate_volatility_scenarios():
    scenarios = generate_volatility_scenarios(0.20)

    assert scenarios == [
        0.10,
        0.15,
        0.20,
        0.25,
        0.30,
    ]


def test_calculate_pnl_matrix():
    matrix = calculate_pnl_matrix(
        option_type="Call",
        spot=100.0,
        strike=100.0,
        volatility=0.20,
        rate=0.05,
        maturity=1.0,
        entry_price=5.0,
        quantity=100,
        position="Long",
    )

    assert len(matrix) == 5
    assert all(len(row) == 5 for row in matrix)

    # Higher spot should generally increase call P&L.
    assert matrix[0][2] < matrix[2][2] < matrix[4][2]


def test_calculate_delta_matrix():
    matrix = calculate_greek_matrix(
        greek="delta",
        option_type="Call",
        spot=100.0,
        strike=100.0,
        volatility=0.20,
        rate=0.05,
        maturity=1.0,
        quantity=100,
        position="Long",
    )

    assert len(matrix) == 5
    assert all(len(row) == 5 for row in matrix)

    # Call delta should generally increase as spot increases.
    assert matrix[0][2] < matrix[2][2] < matrix[4][2]


def test_calculate_vega_matrix():
    matrix = calculate_greek_matrix(
        greek="vega",
        option_type="Call",
        spot=100.0,
        strike=100.0,
        volatility=0.20,
        rate=0.05,
        maturity=1.0,
        quantity=100,
        position="Long",
    )

    assert len(matrix) == 5
    assert all(len(row) == 5 for row in matrix)
    assert all(value >= 0 for row in matrix for value in row)

def test_low_volatility_scenarios_remain_positive_and_distinct():
    scenarios = generate_volatility_scenarios(0.02)

    assert len(scenarios) == 5
    assert all(value > 0 for value in scenarios)
    assert scenarios == [0.01, 0.015, 0.02, 0.025, 0.03]
    assert len(set(scenarios)) == 5


def test_low_volatility_sensitivity_labels_match_actual_scenarios():
    from backend.app.sensitivity.calculator import calculate_volatility_sensitivity

    result = calculate_volatility_sensitivity(
        option_type="Call",
        spot=100.0,
        strike=100.0,
        volatility=0.02,
        rate=0.05,
        maturity=1.0,
        entry_price=1.0,
        quantity=1,
        position="Long",
    )

    assert len(result["volatilities"]) == 5
    assert all(value > 0 for value in result["volatilities"])
    assert result["variations"] == [
        round(value - 0.02, 10) for value in result["volatilities"]
    ]
    assert len(result["pnl"]) == 5


def test_zero_base_volatility_is_rejected():
    import pytest

    with pytest.raises(ValueError, match="Volatility must be greater than zero"):
        generate_volatility_scenarios(0.0)
