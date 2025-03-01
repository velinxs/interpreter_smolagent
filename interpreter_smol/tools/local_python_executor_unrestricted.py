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
    Handles both expressions and statements safely.
    """
    if state is None:
        state = {}
    if static_tools is None:
        static_tools = {}
    if custom_tools is None:
        custom_tools = {}

    # Merge tools into state
    exec_globals = {**BASE_PYTHON_TOOLS, **static_tools, **custom_tools, **state}
    
    try:
        # Try to evaluate as expression first
        tree = ast.parse(code, mode='eval')
        result = eval(code, exec_globals)
        return result, state
    except SyntaxError:
        try:
            # If not an expression, execute as statements
            exec(code, exec_globals)
            # Return None for statements and update state
            state.update({k: v for k, v in exec_globals.items() if k not in BASE_PYTHON_TOOLS})
            return None, state
        except Exception as e:
            raise InterpreterError(f"Error executing code: {str(e)}")