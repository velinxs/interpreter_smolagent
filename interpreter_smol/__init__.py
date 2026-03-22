"""
interpreter-smol - Open Interpreter-like CLI built on SmolaGents

A beautiful, powerful AI code interpreter with:
- Rich terminal UI with syntax highlighting
- Multi-model support (Gemini, OpenAI, Anthropic, HuggingFace)
- Code execution with system access
- Conversation history
- Shell command integration
"""

from interpreter_smol.core.interpreter import Interpreter, ConversationHistory, main
from interpreter_smol.core.ui import InterpreterUI, HAS_RICH

__version__ = "0.3.0"

__all__ = [
    "Interpreter",
    "ConversationHistory",
    "InterpreterUI",
    "HAS_RICH",
    "main",
    "__version__"
]
