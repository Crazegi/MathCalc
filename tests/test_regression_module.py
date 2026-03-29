import math
from src.engine.math_engine import MathEngine


def test_linear_regression():
    engine = MathEngine()
    points = [(0, 1), (1, 2), (2, 2.9), (3, 4.1)]
    props = engine.linear_regression(points)
    assert math.isclose(props['slope'], 1.03, rel_tol=0.05)
    assert math.isclose(props['intercept'], 0.95, rel_tol=0.1)


def test_monte_carlo_probability():
    engine = MathEngine()
    p = engine.monte_carlo_probability(lambda: 1, trials=100)
    assert p == 1.0
    p2 = engine.monte_carlo_probability(lambda: 0, trials=100)
    assert p2 == 0.0
