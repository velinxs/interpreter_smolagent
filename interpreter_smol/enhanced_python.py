"""Enhanced unrestricted Python interpreter with guaranteed system access."""

import os
import sys
import subprocess
import importlib
from typing import Any, Dict, List, Optional, Union
from smolagents.default_tools import PythonInterpreterTool
from smolagents.local_python_executor import evaluate_python_code, BASE_PYTHON_TOOLS

class EnhancedPythonInterpreter(PythonInterpreterTool):
    """A Python interpreter with guaranteed full system access and persistence."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.description = "A Python interpreter with full system access, file operations, and subprocess capabilities."
        
        # Create a more comprehensive set of system tools
        self.base_python_tools = BASE_PYTHON_TOOLS.copy()
        
        # Add system modules
        self.base_python_tools.update({
            "os": os,
            "sys": sys,
            "subprocess": subprocess,
            "open": open,
            "exec": exec,
            "eval": eval,
            "importlib": importlib,
            "__import__": __import__,
        })
        
        # Add a helper function to run shell commands
        def run_shell(cmd, capture_output=True, text=True, shell=True):
            """Run a shell command and return the result."""
            result = subprocess.run(cmd, capture_output=capture_output, text=text, shell=shell)
            return {
                "returncode": result.returncode,
                "stdout": result.stdout if capture_output else "",
                "stderr": result.stderr if capture_output else ""
            }
        
        self.base_python_tools["run_shell"] = run_shell
        
        # Add a helper to write files easily
        def write_file(path, content, mode='w'):
            """Write content to a file."""
            with open(path, mode) as f:
                f.write(content)
            return f"File written to {path}"
        
        self.base_python_tools["write_file"] = write_file
        
        # Add a helper to read files easily
        def read_file(path, mode='r'):
            """Read content from a file."""
            with open(path, mode) as f:
                return f.read()
        
        self.base_python_tools["read_file"] = read_file
    
    def forward(self, code: str) -> str:
        """Execute Python code with full system access."""
        # Create initial state with print capture
        state: Dict[str, Any] = {}
        state["_print_outputs"] = ""
        
        # Execute with all restrictions disabled
        try:
            output = str(
                evaluate_python_code(
                    code,
                    state=state,
                    static_tools=self.base_python_tools,
                    authorized_imports="*",  # Allow all imports
                )[0]
            )
            
            return f"Stdout:\n{str(state['_print_outputs'])}\nOutput: {output}"
        except Exception as e:
            error_msg = f"Error executing code: {str(e)}"
            return f"Stdout:\n{str(state.get('_print_outputs', ''))}\nError: {error_msg}"