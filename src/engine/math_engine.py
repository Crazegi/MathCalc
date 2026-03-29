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
