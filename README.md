# MathTeach — Math Calculator & Tutor (Phase G)

MathTeach is a Python desktop learning application built with PySide6 that provides a complete interactive math curriculum experience for Polish Matura base-level topics. It includes algebra, geometry, calculus, trigonometry, stereo-metry, statistics, regression, and probability, with both theory and hands-on practice in a single app.

## 🌟 Features

- Startup unit selector: Algebra, Trigonometry, Functions, Probability, Regression, Geometry, Calculus, Stereometry, Statistics, Curriculum
- Central math engine: SymPy parsing, simplification, equation solving, and graph-friendly data generation
- Algebra: expressions, equation solve, plot functions, batch plot, 3D equation parsing to geometry
- Geometry: interactive QGraphicsScene (points, lines, circles), angle measurement, triangle analysis, hints, practice problems
- Calculus: derivative, integral, limit, series approximation with step traces
- Trigonometry: evaluate trig expressions, identity simplification and verification
- Stereometry: volumes/areas (prism, pyramid, cylinder, cone, sphere)
- Statistics: mean, median, mode, standard deviation
- Functions: quadratic analysis (a, b, c, vertex, discriminant, roots, parabola direction)
- Probability: binomial PMF/CDF, normal PDF/CDF
- Regression: least-squares line fitting + scatter/line overlay with pyqtgraph + 3D visualization via pyqtgraph.opengl
- Curriculum mode: XML curriculum from `list.xml`, search, progress checkboxes, retained progress (`curriculum_progress.json`), topic-driven module routing
- Practice mode: auto-generated questions + graded answer checking
- Monte Carlo simulation module (coin toss estimates)
- Packaging support via PyInstaller (`package.py`)

## 🚀 Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## 🧪 Running tests

```bash
python -m pytest -q
```

## 🗂 Project layout

- `main.py` — entry point
- `requirements.txt` — dependencies (PySide6, sympy, pyqtgraph, numpy, pytest, pyinstaller)
- `package.py` — PyInstaller helper
- `.gitignore` — IDE + build artifacts
- `list.xml` — curriculum content (Polish Matura topics)
- `src/engine/math_engine.py` — computation core and curriculum question generators
- `src/ui/startup.py` — unit selection screen
- `src/ui/main_window.py` — stacked view and routing for module components
- `src/modules/algebra/widget.py` — algebra operations and plotting
- `src/modules/geometry/widget.py` — interactive geometry canvas and proofs
- `src/modules/calculus/widget.py` — calculus operators
- `src/modules/trigonometry/widget.py` — trig evaluation and identities
- `src/modules/functions/widget.py` — function + quadratic analytic tool
- `src/modules/probability/widget.py` — distribution calculators
- `src/modules/regression/widget.py` — regression + Monte Carlo + plotting
- `src/modules/stereometry/widget.py` — 3D solid formulas
- `src/modules/statistics/widget.py` — basic descriptive stats
- `src/modules/curriculum/widget.py` — curriculum planner + progressive workflow
- `tests/test_math_engine.py` — math engine unit tests
- `tests/test_regression_module.py` — regression and Monte Carlo tests

## 🛠 Packaging (Phase G)

To build a single executable:

```bash
python package.py
```

Output: `dist/MathTeach.exe` (Windows) with PyInstaller `--onefile --windowed`.

## 🔄 Workflow

1. Launch app, select unit/topic.
2. For curriculum mode, search or click topic, mark progress.
3. Solve problems inline, check answers, use right-side hints.
4. Use regression mode for scatter vs best-fit line (2D + 3D). 
5. Save progress automatically via `curriculum_progress.json`.

## 🧩 Notes

- `pytest` present in `requirements.txt` for test environment validation.
- `pyinstaller` in `requirements.txt` + `package.py` for distribution build.

## 📈 Phase path

- Phase A: curriculum navigation & topic mapping
- Phase B: trig/stereo/stat topic support + files
- Phase C: practice generators + answer checking + persistence
- Phase D: advanced function analysis + distribution utilities
- Phase E: regression & Monte Carlo simulation
- Phase G: packaging + polishing + comprehensive README

---

Enjoy building and teaching math with MathTeach! Feel free to extend with custom lesson templates, localized translations, and cloud sync for multi-device progress.

