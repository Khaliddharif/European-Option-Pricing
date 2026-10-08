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
        85.0,
        90.0,
        95.0,
        100.0,
        105.0,
        110.0,
        115.0,
        120.0,
    ]






from backend.app.sensitivity.calculator import (
    generate_spot_scenarios,
    generate_volatility_scenarios,
)


def test_generate_volatility_scenarios():
    scenarios = generate_volatility_scenarios(0.20)

    assert scenarios == [
        0.18,
        0.19,
        0.20,
        0.21,
        0.22,
    ]



from backend.app.sensitivity.calculator import (
    generate_spot_scenarios,
    generate_volatility_scenarios,
    calculate_pnl_matrix,
)


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

    assert len(matrix) == 9
    assert all(len(row) == 5 for row in matrix)

    # Higher spot should generally increase call P&L.
    assert matrix[0][2] < matrix[4][2] < matrix[8][2]




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

    assert len(matrix) == 9
    assert all(len(row) == 5 for row in matrix)

    # Call delta should generally increase as spot increases.
    assert matrix[0][2] < matrix[4][2] < matrix[8][2]


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

    assert len(matrix) == 9
    assert all(len(row) == 5 for row in matrix)
    assert all(value >= 0 for row in matrix for value in row)