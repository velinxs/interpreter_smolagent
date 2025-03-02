"""
Local modified version of key smolagents components.
See CUSTOM_NOTES.md for details.
"""

from .agents import CodeAgent
from .local_python_executor import evaluate_python_code, BASE_PYTHON_TOOLS

__all__ = ['CodeAgent', 'evaluate_python_code', 'BASE_PYTHON_TOOLS']