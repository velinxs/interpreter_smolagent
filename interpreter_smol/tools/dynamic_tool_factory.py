"""
Dynamic Tool Factory - MCP-Equivalent for SmolaGents

This module provides the ability to create tools dynamically at runtime,
similar to how MCP (Model Context Protocol) works for Claude, but adapted
for smolagents' Python-based tool system.
"""

import ast
import inspect
import textwrap
from typing import Any, Callable, Dict, List, Optional, Type
from dataclasses import dataclass
from pathlib import Path
import json
import hashlib
import re


@dataclass
class ToolSpec:
    """Specification for a dynamically created tool"""
    name: str
    description: str
    code: str
    inputs: Dict[str, Dict[str, Any]]  # {param_name: {type: str, description: str}}
    output_type: str
    version: str = "1.0.0"
    author: str = "agent"
    test_cases: List[Dict[str, Any]] = None

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "code": self.code,
            "inputs": self.inputs,
            "output_type": self.output_type,
            "version": self.version,
            "author": self.author,
            "test_cases": self.test_cases or []
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ToolSpec":
        return cls(**data)

    def get_hash(self) -> str:
        """Generate unique hash for this tool version"""
        content = f"{self.name}{self.code}{self.version}"
        return hashlib.md5(content.encode()).hexdigest()[:8]


class ToolValidator:
    """Validates tool code for safety and correctness"""

    # Dangerous patterns to watch for (can be disabled for unrestricted mode)
    DANGEROUS_PATTERNS = [
        r'__import__\s*\(',
        r'globals\s*\(\)',
        r'locals\s*\(\)',
        r'compile\s*\(',
        r'eval\s*\(',  # eval in tool definition itself
    ]

    @staticmethod
    def validate_syntax(code: str) -> tuple[bool, Optional[str]]:
        """Validate Python syntax"""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error: {e}"

    @staticmethod
    def validate_function_signature(code: str, expected_name: str) -> tuple[bool, Optional[str]]:
        """Ensure the code defines a function with the expected name"""
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

            if not functions:
                return False, "No function definition found"

            main_func = functions[0]  # Get the first/main function
            if main_func.name != expected_name:
                return False, f"Function name '{main_func.name}' doesn't match expected '{expected_name}'"

            return True, None
        except Exception as e:
            return False, f"Error parsing function: {e}"

    @staticmethod
    def check_dangerous_patterns(code: str, strict: bool = False) -> tuple[bool, Optional[str]]:
        """Check for potentially dangerous code patterns"""
        if not strict:
            return True, None  # Skip in unrestricted mode

        for pattern in ToolValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, code):
                return False, f"Dangerous pattern detected: {pattern}"

        return True, None

    @staticmethod
    def extract_docstring(code: str) -> Optional[str]:
        """Extract docstring from function"""
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            if functions and ast.get_docstring(functions[0]):
                return ast.get_docstring(functions[0])
        except:
            pass
        return None


class ToolFactory:
    """Factory for creating tools dynamically at runtime"""

    def __init__(self, strict_mode: bool = False, verbose: bool = False):
        """
        Initialize ToolFactory

        Args:
            strict_mode: If True, enforce safety checks. If False, allow unrestricted code.
            verbose: If True, print detailed information
        """
        self.strict_mode = strict_mode
        self.verbose = verbose
        self._created_tools: Dict[str, Type] = {}

    def create_tool_from_code(
        self,
        name: str,
        code: str,
        description: Optional[str] = None,
        inputs: Optional[Dict[str, Dict[str, Any]]] = None,
        output_type: str = "string",
        test_before_register: bool = True
    ) -> tuple[Optional[Type], Optional[str]]:
        """
        Create a tool from Python code

        Args:
            name: Tool name (should match function name)
            code: Python code defining the tool function
            description: Tool description (extracted from docstring if not provided)
            inputs: Input parameter specifications
            output_type: Output type specification
            test_before_register: Whether to test the tool before registering

        Returns:
            Tuple of (Tool class, error message). Tool class is None if creation failed.
        """
        if self.verbose:
            print(f"[ToolFactory] Creating tool '{name}'...")

        # Validate syntax
        valid, error = ToolValidator.validate_syntax(code)
        if not valid:
            return None, error

        # Validate function signature
        valid, error = ToolValidator.validate_function_signature(code, name)
        if not valid:
            return None, error

        # Check dangerous patterns if in strict mode
        valid, error = ToolValidator.check_dangerous_patterns(code, self.strict_mode)
        if not valid:
            return None, error

        # Extract description from docstring if not provided
        if description is None:
            description = ToolValidator.extract_docstring(code) or f"Dynamically created tool: {name}"

        # Auto-detect inputs if not provided
        if inputs is None:
            inputs = self._extract_inputs_from_code(code, name)

        # Create the tool class
        try:
            tool_class = self._build_tool_class(name, code, description, inputs, output_type)

            # Test the tool if requested
            if test_before_register:
                test_result, test_error = self._test_tool(tool_class)
                if not test_result:
                    return None, f"Tool test failed: {test_error}"

            self._created_tools[name] = tool_class

            if self.verbose:
                print(f"[ToolFactory] Successfully created tool '{name}'")

            return tool_class, None

        except Exception as e:
            return None, f"Error creating tool: {e}"

    def create_tool_from_spec(self, spec: ToolSpec) -> tuple[Optional[Type], Optional[str]]:
        """Create a tool from a ToolSpec"""
        return self.create_tool_from_code(
            name=spec.name,
            code=spec.code,
            description=spec.description,
            inputs=spec.inputs,
            output_type=spec.output_type,
            test_before_register=bool(spec.test_cases)
        )

    def _extract_inputs_from_code(self, code: str, func_name: str) -> Dict[str, Dict[str, Any]]:
        """Extract input parameters from function signature"""
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            func = functions[0]

            inputs = {}
            for arg in func.args.args:
                arg_name = arg.arg
                arg_type = "string"  # Default type

                # Try to get type from annotation
                if arg.annotation:
                    annotation = ast.unparse(arg.annotation)
                    arg_type = self._map_python_type_to_tool_type(annotation)

                inputs[arg_name] = {
                    "type": arg_type,
                    "description": f"Parameter {arg_name}"
                }

            return inputs

        except Exception as e:
            if self.verbose:
                print(f"[ToolFactory] Warning: Could not extract inputs: {e}")
            return {}

    def _map_python_type_to_tool_type(self, python_type: str) -> str:
        """Map Python type annotations to tool types"""
        type_map = {
            "str": "string",
            "int": "integer",
            "float": "number",
            "bool": "boolean",
            "list": "array",
            "dict": "object",
            "List": "array",
            "Dict": "object",
            "Any": "any"
        }
        return type_map.get(python_type, "string")

    def _build_tool_class(
        self,
        name: str,
        code: str,
        description: str,
        inputs: Dict[str, Dict[str, Any]],
        output_type: str
    ) -> Type:
        """Build a Tool class from the specifications"""
        from ..smolagents.src.smolagents import Tool

        # Create a namespace for executing the function code
        namespace = {
            '__name__': f'dynamic_tool_{name}',
            '__builtins__': __builtins__,
        }

        # Add common imports that tools might need
        exec("import os", namespace)
        exec("import sys", namespace)
        exec("import json", namespace)
        exec("import re", namespace)
        exec("from pathlib import Path", namespace)

        # Execute the function code to get the function object
        exec(code, namespace)
        func = namespace[name]

        # Create the Tool class
        class DynamicTool(Tool):
            name = name
            description = description
            inputs = inputs
            output_type = output_type

            def forward(self, **kwargs):
                return func(**kwargs)

        # Set a better class name
        DynamicTool.__name__ = f"{name.title().replace('_', '')}Tool"
        DynamicTool.__qualname__ = DynamicTool.__name__

        return DynamicTool

    def _test_tool(self, tool_class: Type) -> tuple[bool, Optional[str]]:
        """Test that a tool can be instantiated"""
        try:
            tool_instance = tool_class()
            # Basic instantiation test
            assert hasattr(tool_instance, 'forward')
            assert hasattr(tool_instance, 'name')
            assert hasattr(tool_instance, 'description')
            return True, None
        except Exception as e:
            return False, str(e)

    def get_created_tools(self) -> Dict[str, Type]:
        """Get all created tools"""
        return self._created_tools.copy()

    def clear_tools(self):
        """Clear all created tools"""
        self._created_tools.clear()


class LLMToolGenerator:
    """Generate tool code using an LLM"""

    TOOL_CREATION_PROMPT = """You are a Python tool generator. Create a Python function that satisfies the following requirements:

Task: {task_description}

Requirements:
1. Function name must be: {function_name}
2. Include a clear docstring describing what the function does
3. Use type hints for parameters and return value
4. Handle errors gracefully with try-except blocks
5. Return a result that can be serialized (string, dict, list, etc.)
6. Keep it simple and focused on the specific task
7. Use only standard library imports when possible

Output ONLY the Python function code, nothing else. No explanations, no markdown, just the code.

Example format:
```python
def function_name(param1: str, param2: int) -> str:
    \"\"\"
    Description of what this function does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value
    \"\"\"
    # Implementation here
    return result
```

Now generate the function:"""

    def __init__(self, model):
        """
        Initialize with an LLM model

        Args:
            model: LLM model instance (should have a __call__ method)
        """
        self.model = model

    def generate_tool(
        self,
        task_description: str,
        function_name: Optional[str] = None
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Generate tool code from a natural language description

        Args:
            task_description: Natural language description of what the tool should do
            function_name: Optional function name (will be auto-generated if not provided)

        Returns:
            Tuple of (generated code, error message)
        """
        if function_name is None:
            function_name = self._generate_function_name(task_description)

        prompt = self.TOOL_CREATION_PROMPT.format(
            task_description=task_description,
            function_name=function_name
        )

        try:
            # Generate code using LLM
            response = self.model(prompt)

            # Extract code from response (handle markdown code blocks)
            code = self._extract_code(response)

            return code, None

        except Exception as e:
            return None, f"Error generating tool: {e}"

    def _generate_function_name(self, description: str) -> str:
        """Generate a function name from description"""
        # Simple heuristic: take first few words and make snake_case
        words = description.lower().split()[:3]
        name = '_'.join(word.strip('.,!?') for word in words if word.isalnum())
        return name or "custom_tool"

    def _extract_code(self, response: str) -> str:
        """Extract Python code from LLM response"""
        # Remove markdown code blocks if present
        if '```python' in response:
            code = response.split('```python')[1].split('```')[0]
        elif '```' in response:
            code = response.split('```')[1].split('```')[0]
        else:
            code = response

        return code.strip()


def create_tool_from_description(
    description: str,
    model,
    name: Optional[str] = None,
    factory: Optional[ToolFactory] = None
) -> tuple[Optional[Type], Optional[str]]:
    """
    High-level function to create a tool from natural language description

    Args:
        description: What the tool should do
        model: LLM model for code generation
        name: Optional tool name
        factory: Optional ToolFactory instance (creates one if not provided)

    Returns:
        Tuple of (Tool class, error message)
    """
    if factory is None:
        factory = ToolFactory(strict_mode=False, verbose=True)

    generator = LLMToolGenerator(model)

    # Generate code
    code, error = generator.generate_tool(description, name)
    if error:
        return None, error

    # Create tool from code
    if name is None:
        name = generator._generate_function_name(description)

    tool_class, error = factory.create_tool_from_code(name, code)
    return tool_class, error
