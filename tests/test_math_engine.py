import pytest
import math
from src.engine.math_engine import MathEngine


def test_evaluate_trig_rad():
    engine = MathEngine()
    value, steps = engine.evaluate_trig('sin(x)', 'pi/2', unit='rad')
    assert float(value) == pytest.approx(1.0, rel=1e-6)


def test_simplify_trig():
    engine = MathEngine()
    simplified, steps = engine.simplify_trig('sin(x)**2 + cos(x)**2')
    assert str(simplified) == '1'


def test_verify_trig_identity_true():
    engine = MathEngine()
    valid, steps = engine.verify_trig_identity('sin(x)**2 + cos(x)**2', '1')
    assert valid


def test_calculate_statistics():
    engine = MathEngine()
    stats, steps = engine.calculate_statistics('2,4,4,6')
    assert stats['mean'] == pytest.approx(4.0)
    assert stats['median'] == pytest.approx(4.0)
    assert stats['mode'] == 4


def test_generate_practice_linear_equation():
    engine = MathEngine()
    q, a, hints = engine.generate_practice('2. Equations and Inequalities', 'Linear equations and inequalities with one variable')
    assert 'Solve:' in q
    assert isinstance(a, float)


def test_check_practice_numeric_true():
    engine = MathEngine()
    assert engine.check_practice(5, '5')
    assert engine.check_practice(2.5, '2.5')


def test_check_practice_numeric_false():
    engine = MathEngine()
    assert not engine.check_practice(5, '4')


def test_quadratic_properties():
    engine = MathEngine()
    props = engine.quadratic_properties('x**2 - 4*x + 3')
    assert props['a'] == 1
    assert props['b'] == -4
    assert props['c'] == 3
    assert props['vertex'][0] == 2
    assert props['roots'] == [1, 3]


def test_binomial_distribution():
    engine = MathEngine()
    pmf = engine.binomial_pmf(10, 3, 0.5)
    cdf = engine.binomial_cdf(10, 3, 0.5)
    assert 0 < pmf < 1
    assert 0 < cdf <= 1


def test_normal_distribution():
    engine = MathEngine()
    pdf = engine.normal_pdf(0, 0, 1)
    cdf = engine.normal_cdf(0, 0, 1)
    assert pdf == pytest.approx(1.0 / math.sqrt(2 * math.pi), rel=1e-6)
    assert cdf == pytest.approx(0.5, rel=1e-6)
