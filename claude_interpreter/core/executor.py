"""Lightweight Python code executor with stdout/stderr capture."""

import builtins
import io
import sys
import os
import subprocess
import traceback
from typing import Any, Dict, Optional, Tuple


class CodeExecutor:
    """Executes Python code blocks with persistent state and output capture."""

    def __init__(self):
        self.globals: Dict[str, Any] = {
            "__builtins__": builtins,
            "os": os,
            "sys": sys,
            "subprocess": subprocess,
        }

    def run(self, code: str) -> Tuple[Optional[str], Optional[str]]:
        """Run Python code, return (stdout, stderr). Either may be None."""
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()
        old_stdout, old_stderr = sys.stdout, sys.stderr

        try:
            sys.stdout = stdout_buf
            sys.stderr = stderr_buf

            try:
                result = eval(compile(code, "<interpreter>", "eval"), self.globals)
                if result is not None:
                    print(repr(result))
            except SyntaxError:
                compiled = compile(code, "<interpreter>", "exec")
                builtins.exec(compiled, self.globals)

        except Exception:
            traceback.print_exc(file=stderr_buf)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        stdout = stdout_buf.getvalue() or None
        stderr = stderr_buf.getvalue() or None
        return stdout, stderr
