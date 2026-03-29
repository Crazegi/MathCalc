import subprocess

"""Packaging helper for MathTeach.
Usage:
    python package.py
"""

entry_script = 'main.py'

def build():
    cmd = [
        'pyinstaller',
        '--onefile',
        '--noconfirm',
        '--windowed',
        '--name', 'MathTeach',
        entry_script,
    ]
    subprocess.run(cmd, check=True)

if __name__ == '__main__':
    build()
