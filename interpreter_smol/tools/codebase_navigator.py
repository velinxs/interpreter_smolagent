"""
Codebase Navigator - Self-awareness tools for the agent

Provides tools for the agent to introspect and understand its own codebase.
Similar to how a developer navigates code, but automated.
"""

import os
import ast
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
import subprocess
import re


class CodebaseNavigator:
    """
    Tools for navigating and introspecting the codebase

    Allows the agent to:
    - List files and directories
    - Read its own source code
    - Search for patterns
    - Find function/class definitions
    - Analyze dependencies
    """

    def __init__(self, project_root: Optional[Path] = None, verbose: bool = False):
        """
        Initialize CodebaseNavigator

        Args:
            project_root: Root directory of the project (auto-detected if not provided)
            verbose: Print detailed information
        """
        if project_root is None:
            # Try to find project root (directory with setup.py or .git)
            current = Path.cwd()
            while current != current.parent:
                if (current / "setup.py").exists() or (current / ".git").exists():
                    project_root = current
                    break
                current = current.parent

            if project_root is None:
                project_root = Path.cwd()

        self.project_root = Path(project_root)
        self.verbose = verbose

    def list_files(
        self,
        directory: Optional[str] = None,
        pattern: Optional[str] = None,
        recursive: bool = True
    ) -> List[str]:
        """
        List files in a directory

        Args:
            directory: Directory to list (relative to project root, or absolute)
            pattern: Optional glob pattern (e.g., "*.py")
            recursive: Whether to search recursively

        Returns:
            List of file paths
        """
        if directory is None:
            search_dir = self.project_root
        else:
            search_dir = self.project_root / directory
            if not search_dir.exists():
                search_dir = Path(directory)  # Try as absolute path

        if not search_dir.exists():
            return []

        if pattern:
            if recursive:
                files = list(search_dir.rglob(pattern))
            else:
                files = list(search_dir.glob(pattern))
        else:
            if recursive:
                files = [f for f in search_dir.rglob("*") if f.is_file()]
            else:
                files = [f for f in search_dir.glob("*") if f.is_file()]

        # Convert to relative paths
        result = []
        for f in files:
            try:
                rel_path = f.relative_to(self.project_root)
                result.append(str(rel_path))
            except ValueError:
                # File is outside project root
                result.append(str(f))

        return sorted(result)

    def read_file(self, file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> Optional[str]:
        """
        Read a file from the codebase

        Args:
            file_path: Path to file (relative to project root or absolute)
            start_line: Optional starting line number (1-indexed)
            end_line: Optional ending line number (1-indexed)

        Returns:
            File contents or None if file doesn't exist
        """
        # Try relative to project root first
        full_path = self.project_root / file_path
        if not full_path.exists():
            # Try as absolute path
            full_path = Path(file_path)

        if not full_path.exists():
            return None

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                if start_line is not None or end_line is not None:
                    lines = f.readlines()
                    start = (start_line - 1) if start_line else 0
                    end = end_line if end_line else len(lines)
                    return ''.join(lines[start:end])
                else:
                    return f.read()
        except Exception as e:
            if self.verbose:
                print(f"Error reading {file_path}: {e}")
            return None

    def search_code(
        self,
        pattern: str,
        file_pattern: Optional[str] = None,
        case_sensitive: bool = False,
        regex: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for code patterns across the codebase

        Args:
            pattern: Search pattern
            file_pattern: Optional file glob pattern (e.g., "*.py")
            case_sensitive: Whether search is case-sensitive
            regex: Whether pattern is a regex

        Returns:
            List of matches with file, line number, and content
        """
        matches = []

        # Use ripgrep if available (faster), otherwise fall back to Python
        if self._has_ripgrep():
            matches = self._search_with_ripgrep(pattern, file_pattern, case_sensitive, regex)
        else:
            matches = self._search_with_python(pattern, file_pattern, case_sensitive, regex)

        return matches

    def _has_ripgrep(self) -> bool:
        """Check if ripgrep is available"""
        try:
            subprocess.run(['rg', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _search_with_ripgrep(
        self,
        pattern: str,
        file_pattern: Optional[str],
        case_sensitive: bool,
        regex: bool
    ) -> List[Dict[str, Any]]:
        """Search using ripgrep"""
        cmd = ['rg', '--json']

        if not case_sensitive:
            cmd.append('-i')

        if not regex:
            cmd.append('-F')  # Fixed string search

        if file_pattern:
            cmd.extend(['-g', file_pattern])

        cmd.append(pattern)
        cmd.append(str(self.project_root))

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            matches = []

            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    if data.get('type') == 'match':
                        match_data = data['data']
                        file_path = match_data['path']['text']
                        line_number = match_data['line_number']
                        line_text = match_data['lines']['text'].rstrip()

                        # Make path relative to project root
                        try:
                            rel_path = Path(file_path).relative_to(self.project_root)
                            file_path = str(rel_path)
                        except ValueError:
                            pass

                        matches.append({
                            'file': file_path,
                            'line': line_number,
                            'content': line_text
                        })
                except json.JSONDecodeError:
                    continue

            return matches

        except Exception as e:
            if self.verbose:
                print(f"Error with ripgrep search: {e}")
            return []

    def _search_with_python(
        self,
        pattern: str,
        file_pattern: Optional[str],
        case_sensitive: bool,
        regex: bool
    ) -> List[Dict[str, Any]]:
        """Fallback Python-based search"""
        matches = []

        # Get files to search
        if file_pattern:
            files = [self.project_root / f for f in self.list_files(pattern=file_pattern)]
        else:
            files = [self.project_root / f for f in self.list_files(pattern="*.py")]

        # Compile pattern if regex
        if regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            compiled_pattern = re.compile(pattern, flags)
        else:
            search_pattern = pattern if case_sensitive else pattern.lower()

        # Search each file
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line_text = line.rstrip()

                        # Check for match
                        if regex:
                            if compiled_pattern.search(line_text):
                                found = True
                            else:
                                found = False
                        else:
                            check_text = line_text if case_sensitive else line_text.lower()
                            found = search_pattern in check_text

                        if found:
                            rel_path = file_path.relative_to(self.project_root)
                            matches.append({
                                'file': str(rel_path),
                                'line': line_num,
                                'content': line_text
                            })
            except Exception:
                continue

        return matches

    def find_function(self, function_name: str) -> List[Dict[str, Any]]:
        """
        Find function definitions in the codebase

        Args:
            function_name: Name of the function to find

        Returns:
            List of locations where function is defined
        """
        results = []

        for file_path in self.list_files(pattern="*.py"):
            full_path = self.project_root / file_path

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(full_path))

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == function_name:
                        results.append({
                            'file': file_path,
                            'line': node.lineno,
                            'type': 'function',
                            'name': function_name
                        })

            except Exception:
                continue

        return results

    def find_class(self, class_name: str) -> List[Dict[str, Any]]:
        """
        Find class definitions in the codebase

        Args:
            class_name: Name of the class to find

        Returns:
            List of locations where class is defined
        """
        results = []

        for file_path in self.list_files(pattern="*.py"):
            full_path = self.project_root / file_path

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(full_path))

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == class_name:
                        results.append({
                            'file': file_path,
                            'line': node.lineno,
                            'type': 'class',
                            'name': class_name
                        })

            except Exception:
                continue

        return results

    def get_imports(self, file_path: str) -> List[str]:
        """
        Get all imports from a file

        Args:
            file_path: Path to file

        Returns:
            List of imported modules
        """
        full_path = self.project_root / file_path
        if not full_path.exists():
            return []

        imports = []

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

        except Exception:
            pass

        return sorted(set(imports))

    def get_file_structure(self, max_depth: int = 3) -> Dict[str, Any]:
        """
        Get a tree structure of the project

        Args:
            max_depth: Maximum depth to traverse

        Returns:
            Nested dict representing directory structure
        """
        def build_tree(path: Path, depth: int) -> Dict[str, Any]:
            if depth > max_depth:
                return {"...": "max depth reached"}

            tree = {}

            try:
                for item in sorted(path.iterdir()):
                    # Skip hidden files and common ignore patterns
                    if item.name.startswith('.'):
                        continue
                    if item.name in ['__pycache__', 'node_modules', 'venv', '.venv']:
                        continue

                    if item.is_dir():
                        tree[item.name + '/'] = build_tree(item, depth + 1)
                    else:
                        tree[item.name] = "file"

            except PermissionError:
                tree["..."] = "permission denied"

            return tree

        return build_tree(self.project_root, 0)

    def get_function_info(self, file_path: str, function_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a function

        Args:
            file_path: Path to file containing the function
            function_name: Name of the function

        Returns:
            Dict with function info (signature, docstring, body, etc.)
        """
        full_path = self.project_root / file_path
        if not full_path.exists():
            return None

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                source = f.read()
                tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    # Get function signature
                    args = [arg.arg for arg in node.args.args]

                    # Get docstring
                    docstring = ast.get_docstring(node)

                    # Get source code
                    start_line = node.lineno
                    end_line = node.end_lineno
                    lines = source.split('\n')
                    func_source = '\n'.join(lines[start_line - 1:end_line])

                    return {
                        'name': function_name,
                        'file': file_path,
                        'line': start_line,
                        'args': args,
                        'docstring': docstring,
                        'source': func_source
                    }

        except Exception as e:
            if self.verbose:
                print(f"Error getting function info: {e}")

        return None

    def find_usages(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Find where a symbol (function, class, variable) is used

        Args:
            symbol: Symbol to search for

        Returns:
            List of usage locations
        """
        # Simple text search for the symbol
        # Note: This is not perfect (doesn't handle scoping) but good enough for most cases
        return self.search_code(
            pattern=rf'\b{symbol}\b',
            file_pattern="*.py",
            regex=True
        )

    def get_project_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the project structure

        Returns:
            Dict with project statistics
        """
        py_files = self.list_files(pattern="*.py")

        total_lines = 0
        total_functions = 0
        total_classes = 0

        for file_path in py_files:
            full_path = self.project_root / file_path

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                    lines = source.split('\n')
                    total_lines += len(lines)

                    try:
                        tree = ast.parse(source)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                total_functions += 1
                            elif isinstance(node, ast.ClassDef):
                                total_classes += 1
                    except:
                        pass

            except Exception:
                continue

        return {
            'project_root': str(self.project_root),
            'total_python_files': len(py_files),
            'total_lines': total_lines,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'file_structure': self.get_file_structure(max_depth=2)
        }
