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
- `src/engine/math_engine.py` — small SymPy wrapper (analysis, simple steps, plot data)
- `src/ui/*` — startup and main window UI
- `src/modules/algebra/widget.py` — algebra calculator widget

Next steps: polish step generator, add geometry canvas, and author practice problems.
