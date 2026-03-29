# MathTeach — Math Calculator & Tutor (Prototype)

Prototype desktop app (Python) with teaching features: Unit selector, Algebra widget, step explanations, and simple plotting.

Quick start

1. Create a virtual environment and activate it (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
python main.py
```

Project layout

- `main.py` — app entry
- `src/engine/math_engine.py` — SymPy wrapper (analysis, step traces, plot data, trig, stats, practice generator)
- `src/ui/*` — startup and main window UI
- `src/modules/algebra/widget.py` — algebra calculator widget
- `src/modules/geometry/widget.py` — interactive geometry canvas
- `src/modules/calculus/widget.py` — calculus operations (derivative, integral, limit)
- `src/modules/trigonometry/widget.py` — trigonometry practice and identity checking
- `src/modules/stereometry/widget.py` — 3D volume/surface calculators for solids
- `src/modules/statistics/widget.py` — descriptive statistics (mean/median/mode/stddev)
- `src/modules/curriculum/widget.py` — curriculum-guided topic launcher with progress tracking
- `tests/test_math_engine.py` — Phase D test coverage

Phase D features:
- Topic practice generation + answer checking (curriculum flow)
- Stereometry module and statistical toolset
- curriculum progress saved to `curriculum_progress.json`

Run tests

```bash
python -m pytest -q
```

