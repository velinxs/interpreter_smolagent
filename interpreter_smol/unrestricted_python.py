"""Unrestricted Python interpreter for full system access."""

import os
from typing import Any, Dict, List
from smolagents.default_tools import PythonInterpreterTool
from smolagents.local_python_executor import evaluate_python_code, BASE_PYTHON_TOOLS

class UnrestrictedPythonInterpreter(PythonInterpreterTool):
    """A Python interpreter without system access restrictions."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.description = "A Python interpreter with full system access for trusted environments."
        
        # Add system commands to base tools
        self.base_python_tools = BASE_PYTHON_TOOLS.copy()
        self.base_python_tools.update({
            "os": os,
            "open": open,
            "exec": exec,
            "eval": eval,
        })
    
    def forward(self, code: str) -> str:
        # Create initial state with print capture
        state: Dict[str, Any] = {}
        state["_print_outputs"] = ""
        
        # Execute with all restrictions disabled
        output = str(
            evaluate_python_code(
                code,
                state=state,
                static_tools=self.base_python_tools,
                authorized_imports="*",  # Allow all imports
            )[0]
        )
        
        return f"Stdout:\n{str(state['_print_outputs'])}\nOutput: {output}"