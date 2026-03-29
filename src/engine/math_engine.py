from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import sympy as sp

class MathEngine:
    """Small SymPy-based engine: parse, simplify, simple step traces, and plot data."""
    def __init__(self):
        self.sp = sp
        self.transformations = (standard_transformations + (implicit_multiplication_application,))

    def _parse(self, s: str):
        s = s.strip()
        s = s.replace('^', '**')
        try:
            expr = parse_expr(s, transformations=self.transformations)
            return expr
        except Exception:
            try:
                return sp.sympify(s)
            except Exception:
                raise

    def analyze_input(self, s: str):
        s = s.strip()
        if '=' in s:
            left, right = s.split('=', 1)
            lhs = self._parse(left)
            rhs = self._parse(right)
            eq = sp.Eq(lhs, rhs)
            steps = [f"Equation: {sp.pretty(eq)}"]
            diff = sp.simplify(lhs - rhs)
            steps.append(f"Bring terms together: {sp.pretty(diff)}")
            syms = list(eq.free_symbols)
            if syms:
                var = syms[0]
                sol = sp.solve(eq, var)
                steps.append(f"Solve for {var}: {sol}")
                return steps, sol, None
            else:
                steps.append("No symbols to solve for.")
                return steps, str(eq), None
        else:
            expr = self._parse(s)
            simplified = sp.simplify(expr)
            steps = [f"Parsed: {sp.pretty(expr)}", f"Simplified: {sp.pretty(simplified)}"]
            numeric = None
            try:
                numeric_val = sp.N(expr)
                # if it's a number
                if getattr(numeric_val, 'is_real', False) or hasattr(numeric_val, 'is_Number'):
                    numeric = float(numeric_val)
                    steps.append(f"Numeric evaluation: {numeric}")
            except Exception:
                numeric = None
            syms = list(expr.free_symbols)
            plot_data = None
            if len(syms) == 1:
                var = list(syms)[0]
                try:
                    import numpy as np
                    f = sp.lambdify(var, expr, 'numpy')
                    x = np.linspace(-10, 10, 400)
                    y = f(x)
                    plot_data = (x, y)
                except Exception:
                    plot_data = None
            display_result = numeric if numeric is not None else simplified
            return steps, display_result, plot_data

    def evaluate_trig(self, expression: str, value=None, unit='rad'):
        expr = self._parse(expression)
        steps = [f"Parsed: {sp.pretty(expr)}"]
        try:
            if value is not None and value != '':
                x = sp.symbols('x')
                val_expr = self._parse(value)
                if unit == 'deg':
                    val_expr = val_expr * sp.pi / 180
                evaluated = expr.subs(x, val_expr)
            else:
                evaluated = expr
            simplified = sp.simplify(evaluated)
            numeric = sp.N(simplified)
            steps.append(f"Simplified: {sp.pretty(simplified)}")
            steps.append(f"Numeric: {sp.pretty(numeric)}")
            return numeric, steps
        except Exception as e:
            raise

    def simplify_trig(self, expression: str):
        expr = self._parse(expression)
        steps = [f"Parsed: {sp.pretty(expr)}"]
        simplified = sp.trigsimp(expr)
        steps.append(f"Trig simplification: {sp.pretty(simplified)}")
        return simplified, steps

    def verify_trig_identity(self, a: str, b: str):
        expr_a = self._parse(a)
        expr_b = self._parse(b)
        steps = [f"A: {sp.pretty(expr_a)}", f"B: {sp.pretty(expr_b)}"]
        diff = sp.simplify(expr_a - expr_b)
        steps.append(f"Difference simplified: {sp.pretty(diff)}")
        valid = sp.simplify(diff) == 0
        return valid, steps

    def calculate_statistics(self, values):
        # values: list of numbers or comma-separated string
        if isinstance(values, str):
            values = [v.strip() for v in values.split(',') if v.strip()]
            values = [float(v) for v in values]
        n = len(values)
        if n == 0:
            return {}, ["No values provided"]
        mean = sum(values) / n
        sorted_vals = sorted(values)
        median = sorted_vals[n//2] if n % 2 == 1 else (sorted_vals[n//2-1] + sorted_vals[n//2]) / 2
        mode = max(set(values), key=values.count)
        variance = sum((x - mean) ** 2 for x in values) / n
        stddev = variance ** 0.5
        steps = [f"Mean: {mean}", f"Median: {median}", f"Mode: {mode}", f"Stddev: {stddev}"]
        stats = {"mean": mean, "median": median, "mode": mode, "stddev": stddev}
        return stats, steps

    def quadratic_properties(self, formula):
        x = sp.symbols('x')
        expr = self._parse(formula)
        a = sp.simplify(expr.coeff(x, 2))
        b = sp.simplify(expr.coeff(x, 1))
        c = sp.simplify(expr.coeff(x, 0))
        h = -b / (2*a) if a != 0 else None
        k = expr.subs(x, h) if h is not None else None
        vertex = (h, k) if h is not None else None
        discriminant = b**2 - 4*a*c
        roots = sp.solve(sp.Eq(expr, 0), x)
        properties = {
            'a': float(a), 'b': float(b), 'c': float(c),
            'vertex': vertex, 'discriminant': float(discriminant), 'roots': roots,
            'parabola': 'up' if a > 0 else 'down' if a < 0 else 'linear'
        }
        return properties

    def binomial_pmf(self, n, k, p):
        comb = math.comb(n, k)
        return comb * (p**k) * ((1-p)**(n-k))

    def binomial_cdf(self, n, k, p):
        return sum(self.binomial_pmf(n, i, p) for i in range(0, k+1))

    def normal_pdf(self, x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
        return (1.0 / (sigma * math.sqrt(2*math.pi))) * math.exp(-0.5 * ((x-mu)/sigma)**2)

    def normal_cdf(self, x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
        return 0.5 * (1 + math.erf((x-mu)/(sigma*math.sqrt(2))))

    def generate_practice(self, section, topic):
        # simple seeded problem generation for topics
        import random
        section_low = section.lower()
        t_low = topic.lower()
        if 'linear equation' in t_low or 'linear equations' in t_low:
            a = random.randint(1, 9)
            b = random.randint(-9, 9)
            c = random.randint(-9, 9)
            question = f"Solve: {a}*x + {b} = {c}"
            answer = (c - b) / a
            return question, answer, [f"Move {b} to right side", f"Divide by {a}"]
        if 'quadratic' in t_low or 'parabol' in t_low:
            a = random.randint(1, 4)
            b = random.randint(-5, 5)
            c = random.randint(-5, 5)
            question = f"Solve: {a}*x**2 + {b}*x + {c} = 0"
            sol = sp.solve(sp.Eq(a*sp.symbols('x')**2 + b*sp.symbols('x') + c, 0), sp.symbols('x'))
            return question, sol, ["Apply quadratic formula (or factoring)"]
        if 'trigonometry' in section_low or 'sin' in t_low or 'cos' in t_low or 'tan' in t_low:
            question = "Evaluate: sin(pi/6) + cos(pi/3)"
            answer = sp.sin(sp.pi/6) + sp.cos(sp.pi/3)
            return question, answer, ["Use known sin/cos values"]
        if 'sequence' in section_low:
            a = random.randint(1, 10)
            d = random.randint(1, 9)
            n = random.randint(5, 12)
            question = f"Find {n}-th term of arithmetic sequence with a1={a}, d={d}."
            answer = a + (n-1)*d
            return question, answer, ["Use formula a_n = a1 + (n-1)*d"]
        if 'probability' in section_low or 'statistics' in section_low:
            question = "Find mean of 2,4,6,8,10"
            answer = 6
            return question, answer, ["Sum values and divide by count"]
        return "No practice available", None, ["Topic too advanced for generator"]

    def check_practice(self, expected, response):
        try:
            if expected is None:
                return False
            if isinstance(expected, (list, tuple)):
                resp = self._parse(response)
                return set(expected) == set(resp) if isinstance(resp, (list, tuple)) else False
            resp = float(response)
            return abs(resp - float(expected)) < 1e-6
        except Exception:
            return False
