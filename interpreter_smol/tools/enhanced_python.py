"""Enhanced unrestricted Python interpreter with guaranteed system access."""

import os
import sys
import subprocess
import importlib
import builtins
import io
import requests
import json
import datetime
import re
import urllib
import html
import time
import random
import tempfile
import shutil
import glob
import zipfile
import bs4
from PIL import Image
from bs4 import BeautifulSoup
from typing import Any, Dict, List, Optional, Tuple
from smolagents.tools import Tool
from local_python_executor_unrestricted import evaluate_python_code, BASE_PYTHON_TOOLS

class EnhancedPythonInterpreter(Tool):
    """A Python interpreter with full system access and persistence."""

    def __init__(self, authorized_imports: Optional[List[str]] = None):
        """Initialize the unrestricted Python interpreter.

        Args:
            authorized_imports: List of modules to allow importing (ignored here - we allow everything).
        """
        super().__init__()
        self.name = "python_interpreter"
        self.description = (
            "A Python interpreter with full system access, file operations, "
            "and subprocess capabilities."
        )

        # We declare just one input "code", but we'll skip signature validation so we can use **kwargs
        self.inputs = {
            "code": {
                "type": "string",
                "description": "The Python code to execute"
            }
        }
        self.output_type = "string"

        # This bypasses the library's strict forward() signature checks
        self.skip_forward_signature_validation = True

        self.is_initialized = True
        self.history = []
        self.verbosity_level = 1

        # Start with the base Python tools
        self.base_python_tools = BASE_PYTHON_TOOLS.copy()

        # Add full system modules
        self.base_python_tools.update({
            "os": os,
            "sys": sys,
            "subprocess": subprocess,
            "open": open,
            "exec": exec,
            "eval": eval,
            "importlib": importlib,
            "__import__": __import__,
            "requests": requests,
            "json": json,
            "datetime": datetime,
            "re": re,
            "urllib": urllib,
            "html": html,
            "time": time,
            "random": random,
            "tempfile": tempfile,
            "BeautifulSoup": BeautifulSoup,
            "shutil": shutil,
            "glob": glob,
            "zipfile": zipfile,
            "bs4": bs4,
            "Image": Image,
            "PIL": Image,
        })

        # Helper to run shell commands
        def run_shell(cmd, capture_output=True, text=True, shell=True):
            result = subprocess.run(cmd, capture_output=capture_output, text=text, shell=shell)
            return {
                "returncode": result.returncode,
                "stdout": result.stdout if capture_output else "",
                "stderr": result.stderr if capture_output else ""
            }
        self.base_python_tools["run_shell"] = run_shell

        # Helper to write files easily
        def write_file(path, content, mode='w'):
            with open(path, mode) as f:
                f.write(content)
            return f"File written to {path}"
        self.base_python_tools["write_file"] = write_file

        # Helper to read files easily
        def read_file(path, mode='r'):
            with open(path, mode) as f:
                return f.read()
        self.base_python_tools["read_file"] = read_file

    def forward(self, **kwargs) -> Tuple[Any, Dict[str, Any]]:
            """Execute Python code with full system access, capturing prints."""
            # The user code is passed in with the key "code"
            code = kwargs.get("code", "")

            # We'll capture any print statements to this buffer
            buffer = io.StringIO()
            original_print = builtins.print

            def custom_print(*args, **print_kwargs):
                # This calls real 'print' so you still see output in logs
                original_print(*args, **print_kwargs)
                # Also record it in the buffer
                print(*args, **print_kwargs, file=buffer)

            # Temporarily override builtins.print
            builtins.print = custom_print

            state: Dict[str, Any] = {}
            state["_print_outputs"] = ""

            try:
                # Execute code directly without any restrictions
                exec_globals = {**globals(), **self.base_python_tools, **state}
                # Make sure open() is available and using the built-in function
                exec_globals['open'] = builtins.open
                
                try:
                    # Try to evaluate as expression first
                    result = eval(code, exec_globals)
                except SyntaxError:
                    # If not an expression, execute as statements
                    exec(code, exec_globals)
                    # Update state with any new variables
                    state.update({k: v for k, v in exec_globals.items() 
                                if k not in globals() and k not in self.base_python_tools})
                    result = None
            except Exception as e:
                # If there's an error, revert print and return error tuple
                builtins.print = original_print
                error_msg = f"Error executing code: {str(e)}"
                return None, {"error": error_msg, "stdout": buffer.getvalue()}
            finally:
                # Always restore the original print function
                builtins.print = original_print

            # The captured prints are in buffer
            captured_text = buffer.getvalue()
            
            # Return result and state with stdout
            return result, {"stdout": captured_text.strip(), "state": state}