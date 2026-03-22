"""
interpreter-smol — Open Interpreter-like REPL powered by Claude Code.
"""

from claude_interpreter.core.interpreter import Interpreter, main
from claude_interpreter.core.executor import CodeExecutor

__version__ = "0.4.0"
__all__ = ["Interpreter", "CodeExecutor", "main", "__version__"]
