"""
interpreter_smol - A thin wrapper around SmolaGents that provides an Open-Interpreter-like experience
"""

import os
import sys
import argparse
import importlib.util
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import yaml

# Main SmolaGents imports
from smolagents import CodeAgent
from smolagents.default_tools import TOOL_MAPPING
from interpreter_smol.tools import EnhancedPythonInterpreter

class Interpreter:
    """Simple Open-Interpreter-like interface built on SmolaGents."""
    
    def __init__(
        self, 
        model: str = "gemini",
        model_id: Optional[str] = None,
        api_key: Optional[str] = None,
        tools: List[str] = ["enhanced_python", "web_search"],  # Using our enhanced Python interpreter
        imports: List[str] = ["os", "sys", "numpy", "pandas", "matplotlib.pyplot"],
        temperature: float = 0.7,
        max_tokens: int = 8192,
        verbose: bool = False
    ):
        """Initialize an interpreter with specified model and tools."""
        self.model_type = model
        self.model_id = model_id
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.verbose = verbose
        
        # Initialize model and agent
        self.model = self._initialize_model()
        self.agent = self._initialize_agent(tools, imports)
    
    def _initialize_model(self):
        """Initialize the model based on type."""
        if self.model_type.lower() == "gemini":
            from smolagents import LiteLLMModel
            return LiteLLMModel(
                model_id=self.model_id or "gemini/gemini-2.0-flash",
                api_key=self.api_key or os.environ.get("GOOGLE_API_KEY"),
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        elif self.model_type.lower() == "openai":
            from smolagents import LiteLLMModel
            return LiteLLMModel(
                model_id=self.model_id or "gpt-4o",
                api_key=self.api_key or os.environ.get("OPENAI_API_KEY"),
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        elif self.model_type.lower() == "anthropic":
            from smolagents import LiteLLMModel
            return LiteLLMModel(
                model_id=self.model_id or "claude-3-7-sonnet-latest",
                api_key=self.api_key or os.environ.get("ANTHROPIC_API_KEY"),
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        elif self.model_type.lower() == "hf":
            from smolagents import HfApiModel
            return HfApiModel(
                model_id=self.model_id or "mistralai/Mistral-7B-Instruct-v0.2",
                token=self.api_key or os.environ.get("HF_API_TOKEN"),
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    def _initialize_agent(self, tool_names, imports):
        """Initialize the CodeAgent with specified tools."""
        # Expand imports to include everything needed for system access
        all_imports = imports + [
            "os", "sys", "subprocess", "shutil", "glob", "pathlib", "json", "csv",
            "platform", "pwd", "grp", "tempfile", "io", "stat", "fnmatch", "time",
            "datetime", "calendar", "signal", "threading", "multiprocessing", "socket",
            "requests", "urllib", "ftplib", "ssl", "getpass"
        ]

        tools = []
        for tool_name in tool_names:
            if tool_name == "unrestricted_python" or tool_name == "enhanced_python":
                tool = EnhancedPythonInterpreter(authorized_imports=all_imports)
                tools.append(tool)
            elif tool_name in TOOL_MAPPING:
                tool = TOOL_MAPPING[tool_name]()
                tools.append(tool)
            else:
                available_tools = list(TOOL_MAPPING.keys()) + ["unrestricted_python", "enhanced_python"]
                print(f"Warning: Unknown tool '{tool_name}'. Available tools: {', '.join(available_tools)}")

        # Load custom prompt templates from code_agent.yaml
        prompt_path = Path(__file__).parent.parent / "prompts" / "code_agent.yaml"
        if prompt_path.exists():
            try:
                with open(prompt_path, 'r') as f:
                    prompt_templates = yaml.safe_load(f)
            except Exception as e:
                print(f"Warning: Could not load custom prompt templates: {e}")
                prompt_templates = None
        else:
            prompt_templates = None
            print("Warning: No code_agent.yaml found in prompts directory")

        # Create agent with custom or default prompt
        agent = CodeAgent(
            tools=tools,
            model=self.model,
            additional_authorized_imports=all_imports,
            verbosity_level=2 if self.verbose else 1,
            prompt_templates=prompt_templates  # Use our custom prompts if available
        )
        return agent
    
    def chat(self, initial_prompt: Optional[str] = None):
        """Start an interactive chat session."""
        if initial_prompt:
            self.agent.run(initial_prompt)
        
        try:
            print("Welcome to interpreter-smol! Type 'exit' to quit.")
            while True:
                user_input = input("\n> ")
                if user_input.lower() in ["exit", "quit", "q"]:
                    break
                self.agent.run(user_input, reset=False)
        except KeyboardInterrupt:
            print("\nExiting...")
    
    def run(self, prompt: str):
        """Run a single prompt and return the result."""
        return self.agent.run(prompt)


def main():
    """Command line interface for interpreter-smol."""
    parser = argparse.ArgumentParser(description="interpreter-smol: Open-Interpreter-like CLI built on SmolaGents")
    
    # Simplified CLI arguments
    parser.add_argument("prompt", nargs="?", help="The prompt to run")
    parser.add_argument("--model", "-m", default="gemini", 
                        choices=["gemini", "openai", "anthropic", "hf"],
                        help="Model provider to use")
    parser.add_argument("--model-id", default=None, 
                        help="Specific model ID (defaults to best model for provider)")
    parser.add_argument("--tools", nargs="*", 
                        default=["enhanced_python", "web_search"],
                        help="Tools to enable")
    parser.add_argument("--api-key", "-k", default=None, 
                        help="API key for the model provider")
    parser.add_argument("--imports", nargs="*", 
                        default=["numpy", "pandas", "matplotlib.pyplot"],
                        help="Python imports to allow")
    parser.add_argument("--temperature", "-t", type=float, default=0.7,
                        help="Temperature for generation")
    parser.add_argument("--max-tokens", type=int, default=4096,
                        help="Maximum tokens in response")
    parser.add_argument("-i", "--interactive", action="store_true", 
                        help="Start in interactive mode")
    parser.add_argument("-v", "--verbose", action="store_true", 
                        help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Set up environment variables for API keys if provided
    if args.api_key:
        if args.model.lower() == "gemini":
            os.environ["GOOGLE_API_KEY"] = args.api_key
        elif args.model.lower() == "openai":
            os.environ["OPENAI_API_KEY"] = args.api_key
        elif args.model.lower() == "anthropic":
            os.environ["ANTHROPIC_API_KEY"] = args.api_key
        elif args.model.lower() == "hf":
            os.environ["HF_API_TOKEN"] = args.api_key
    
    try:
        # Initialize the interpreter
        interpreter = Interpreter(
            model=args.model,
            model_id=args.model_id,
            api_key=args.api_key,
            tools=args.tools,
            imports=args.imports,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            verbose=args.verbose
        )
        
        # Run in appropriate mode
        if args.interactive or not args.prompt:
            interpreter.chat(args.prompt)
        else:
            interpreter.run(args.prompt)
            
    except ImportError as e:
        print(f"Error: {e}")
        if "google-genai" in str(e):
            print("Install Google GenAI package with: pip install google-genai")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()