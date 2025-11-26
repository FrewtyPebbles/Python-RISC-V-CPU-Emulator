# setup.py
from setuptools import setup, find_packages
from pathlib import Path

# Find all .py files in src/ (excluding __pycache__)
py_modules = [
    p.stem for p in Path("src").glob("*.py")
]

setup(
    py_modules=py_modules,
)