#!/usr/bin/env python
# coding=utf-8

# Modified version of smolagents' local_python_executor.py with security restrictions removed
import ast
import builtins
import difflib
import inspect
import logging
import math
import re
from collections.abc import Mapping
from importlib import import_module
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd

from smolagents.tools import Tool
from smolagents.utils import BASE_BUILTIN_MODULES, truncate_content

logger = logging.getLogger(__name__)

class InterpreterError(ValueError):
    """An error raised when the interpreter cannot evaluate a Python expression."""
    pass

# Keep basic Python tools that are safe and useful
BASE_PYTHON_TOOLS = {
    "print": print,  # We'll use real print
    "isinstance": isinstance,
    "range": range,
    "float": float,
    "int": int,
    "bool": bool,
    "str": str,
    "set": set,
    "list": list,
    "dict": dict,
    "tuple": tuple,
    "round": round,
    "len": len,
    "sum": sum,
    "max": max,
    "min": min,
    "abs": abs,
    "enumerate": enumerate,
    "zip": zip,
    "reversed": reversed,
    "sorted": sorted,
    "all": all,
    "any": any,
    "map": map,
    "filter": filter,
    "next": next,
    "iter": iter,
    "open": open,  # Add built-in open function
}

def evaluate_python_code(
    code: str,
    state: Optional[Dict[str, Any]] = None,
    static_tools: Optional[Dict[str, Any]] = None,
    custom_tools: Optional[Dict[str, Any]] = None,
    authorized_imports: Optional[Union[str, List[str]]] = None,
) -> Tuple[Any, Dict[str, Any]]:
    """
    Evaluate Python code with direct execution.
    Handles both expressions and statements with full access.
    """
    if state is None:
        state = {}
    if static_tools is None:
        static_tools = {}
    if custom_tools is None:
        custom_tools = {}

    # Create globals with everything including builtins
    exec_globals = {
        **globals(),  # Get all global variables
        **vars(builtins),  # Get ALL builtins including open()
        **BASE_PYTHON_TOOLS,  # Our base tools
        **static_tools,  # Any static tools passed in
        **custom_tools,  # Any custom tools passed in 
        **state,  # Current state
        'open': builtins.open,  # Explicitly ensure open() is available
    }
    
    try:
        # Try direct exec first - most permissive
        exec(code, exec_globals)
        # Get any new variables added to state
        state.update({k: v for k, v in exec_globals.items() 
                     if k not in globals() and 
                     k not in vars(builtins) and
                     k not in BASE_PYTHON_TOOLS})
        # Try to get a result if one was assigned
        result = exec_globals.get('_result', None)
        return result, state
        
    except Exception as exec_error:
        try:
            # If exec failed, try eval as fallback
            result = eval(code, exec_globals)
            return result, state
        except Exception as eval_error:
            # If both fail, raise original exec error
            raise InterpreterError(f"Error executing code: {str(exec_error)}")