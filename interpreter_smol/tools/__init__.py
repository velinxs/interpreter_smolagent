"""Tools package for interpreter_smol."""

from .unrestricted_python import EnhancedPythonInterpreter
from .local_python_executor_unrestricted import evaluate_python_code, BASE_PYTHON_TOOLS

# Alias for compatibility
UnrestrictedPythonInterpreter = EnhancedPythonInterpreter

__all__ = ['EnhancedPythonInterpreter', 'UnrestrictedPythonInterpreter', 'evaluate_python_code', 'BASE_PYTHON_TOOLS']
