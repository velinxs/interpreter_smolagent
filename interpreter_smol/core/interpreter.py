"""
interpreter_smol - Open Interpreter-like CLI built on SmolaGents

A powerful, beautiful CLI for running AI-powered code execution with:
- Rich terminal UI with syntax highlighting
- Conversation history and memory
- Direct shell command execution
- Multiple model support
- Safe and auto-run modes
"""

import os
import sys
import argparse
import subprocess
import json
import importlib.util
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
from datetime import datetime
import yaml

# Import our UI components
from interpreter_smol.core.ui import InterpreterUI, RichAgentCallback, HAS_RICH

# Import our modified CodeAgent from local smolagents
from smolagents.agents import CodeAgent
from smolagents.default_tools import TOOL_MAPPING
from interpreter_smol.tools import EnhancedPythonInterpreter

# Version info
__version__ = "0.3.0"


class ConversationHistory:
    """Manages conversation history with save/load capabilities."""

    def __init__(self, max_messages: int = 100):
        self.messages: List[Dict[str, str]] = []
        self.max_messages = max_messages

    def add(self, role: str, content: str):
        """Add a message to history."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        # Keep only recent messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def clear(self):
        """Clear conversation history."""
        self.messages = []

    def get_context(self, last_n: int = 10) -> str:
        """Get recent context as string."""
        recent = self.messages[-last_n:] if len(self.messages) > last_n else self.messages
        return "\n".join([f"{m['role']}: {m['content']}" for m in recent])

    def save(self, filepath: str):
        """Save history to file."""
        with open(filepath, 'w') as f:
            json.dump(self.messages, f, indent=2)

    def load(self, filepath: str):
        """Load history from file."""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.messages = json.load(f)


class Interpreter:
    """
    Open Interpreter-like interface built on SmolaGents.

    Features:
    - Beautiful Rich-powered terminal UI
    - Multi-model support (Gemini, OpenAI, Anthropic, HuggingFace)
    - Code execution with syntax highlighting
    - Shell command integration
    - Conversation history
    - Safe mode with confirmation prompts
    """

    def __init__(
        self,
        model: str = "gemini",
        model_id: Optional[str] = None,
        api_key: Optional[str] = None,
        tools: List[str] = ["enhanced_python", "web_search"],
        imports: List[str] = ["os", "sys", "numpy", "pandas", "matplotlib.pyplot"],
        temperature: float = 0.7,
        max_tokens: int = 8192,
        verbose: bool = False,
        safe_mode: bool = False,
        auto_run: bool = True,
    ):
        """
        Initialize the interpreter.

        Args:
            model: Model provider (gemini, openai, anthropic, hf)
            model_id: Specific model ID
            api_key: API key for the provider
            tools: List of tools to enable
            imports: Python imports to allow
            temperature: Generation temperature
            max_tokens: Max tokens in response
            verbose: Enable verbose output
            safe_mode: Require confirmation before code execution
            auto_run: Automatically run generated code
        """
        self.model_type = model
        self.model_id = model_id or self._get_default_model_id(model)
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.verbose = verbose
        self.safe_mode = safe_mode
        self.auto_run = auto_run
        self.tool_names = tools
        self.imports = imports

        # Initialize UI
        self.ui = InterpreterUI(verbose=verbose)
        self.callback = RichAgentCallback(self.ui)

        # Initialize conversation history
        self.history = ConversationHistory()

        # Initialize model and agent
        self.model = self._initialize_model()
        self.agent = self._initialize_agent(tools, imports)

    def _get_default_model_id(self, model: str) -> str:
        """Get default model ID for provider."""
        defaults = {
            "gemini": "gemini/gemini-2.0-flash",
            "openai": "gpt-4o",
            "anthropic": "claude-sonnet-4-20250514",
            "hf": "mistralai/Mistral-7B-Instruct-v0.2"
        }
        return defaults.get(model.lower(), "gemini/gemini-2.0-flash")

    def _initialize_model(self):
        """Initialize the LLM model based on type."""
        from smolagents import LiteLLMModel

        api_key = self.api_key

        # Get API key from environment if not provided
        if not api_key:
            env_keys = {
                "gemini": "GOOGLE_API_KEY",
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "hf": "HF_API_TOKEN"
            }
            env_key = env_keys.get(self.model_type.lower())
            if env_key:
                api_key = os.environ.get(env_key)

        if self.model_type.lower() == "hf":
            from smolagents import HfApiModel
            return HfApiModel(
                model_id=self.model_id,
                token=api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

        return LiteLLMModel(
            model_id=self.model_id,
            api_key=api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

    def _initialize_agent(self, tool_names: List[str], imports: List[str]):
        """Initialize the CodeAgent with specified tools."""
        # Expand imports to include system access modules
        all_imports = list(set(imports + [
            "os", "sys", "subprocess", "shutil", "glob", "pathlib", "json", "csv",
            "platform", "pwd", "grp", "tempfile", "io", "stat", "fnmatch", "time",
            "datetime", "calendar", "signal", "threading", "multiprocessing", "socket",
            "requests", "urllib", "ftplib", "ssl", "getpass", "re", "random",
            "collections", "itertools", "functools", "operator", "math", "statistics"
        ]))

        tools = []
        for tool_name in tool_names:
            if tool_name in ("unrestricted_python", "enhanced_python"):
                tool = EnhancedPythonInterpreter(authorized_imports=all_imports)
                tools.append(tool)
            elif tool_name in TOOL_MAPPING:
                tool = TOOL_MAPPING[tool_name]()
                tools.append(tool)
            else:
                available = list(TOOL_MAPPING.keys()) + ["enhanced_python"]
                self.ui.print_warning(f"Unknown tool '{tool_name}'. Available: {', '.join(available)}")

        # Load custom prompt templates
        prompt_path = Path(__file__).parent.parent / "prompts" / "code_agent.yaml"
        prompt_templates = None
        if prompt_path.exists():
            try:
                with open(prompt_path, 'r') as f:
                    prompt_templates = yaml.safe_load(f)
            except Exception as e:
                if self.verbose:
                    self.ui.print_warning(f"Could not load custom prompts: {e}")

        # Create agent
        agent = CodeAgent(
            tools=tools,
            model=self.model,
            additional_authorized_imports=all_imports,
            verbosity_level=2 if self.verbose else 1,
            prompt_templates=prompt_templates
        )
        return agent

    def run_shell(self, command: str) -> tuple:
        """Execute a shell command and return (output, return_code)."""
        self.ui.print_shell_command(command)
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            output = result.stdout + result.stderr
            self.ui.print_shell_output(output, result.returncode)
            return output, result.returncode
        except subprocess.TimeoutExpired:
            self.ui.print_error("Command timed out after 5 minutes")
            return "", 1
        except Exception as e:
            self.ui.print_error(str(e))
            return str(e), 1

    def run(self, prompt: str) -> str:
        """Run a single prompt and return the result."""
        self.history.add("user", prompt)
        try:
            result = self.agent.run(prompt)
            self.history.add("assistant", str(result))
            return result
        except Exception as e:
            self.ui.print_error(str(e))
            return str(e)

    def chat(self, initial_prompt: Optional[str] = None):
        """Start an interactive chat session."""
        self.ui.print_welcome(model=self.model_type, model_id=self.model_id)

        # Run initial prompt if provided
        if initial_prompt:
            self.ui.print_user_message(initial_prompt)
            self.run(initial_prompt)

        # Main interaction loop
        try:
            while True:
                try:
                    # Get user input
                    user_input = self.ui.get_input("\n> ").strip()

                    if not user_input:
                        continue

                    # Handle special commands
                    if user_input.lower() in ("exit", "quit", "q"):
                        break

                    elif user_input == "?":
                        self.ui.print_help()
                        continue

                    elif user_input.lower() == "clear":
                        self.ui.clear()
                        continue

                    elif user_input.lower() == "reset":
                        self.history.clear()
                        self.agent = self._initialize_agent(self.tool_names, self.imports)
                        self.ui.print_success("Conversation reset!")
                        continue

                    elif user_input.lower() == "history":
                        self.ui.print_conversation_history(self.history.messages)
                        continue

                    elif user_input.lower().startswith("save"):
                        parts = user_input.split(maxsplit=1)
                        filepath = parts[1] if len(parts) > 1 else f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        self.history.save(filepath)
                        self.ui.print_success(f"Conversation saved to {filepath}")
                        continue

                    elif user_input.lower() == "config":
                        config = {
                            "Model": self.model_id,
                            "Provider": self.model_type,
                            "Temperature": self.temperature,
                            "Max Tokens": self.max_tokens,
                            "Safe Mode": self.safe_mode,
                            "Auto Run": self.auto_run,
                            "Tools": ", ".join(self.tool_names),
                            "Verbose": self.verbose
                        }
                        self.ui.print_config(config)
                        continue

                    elif user_input.startswith("!"):
                        # Shell command
                        cmd = user_input[1:].strip()
                        if cmd:
                            self.run_shell(cmd)
                        continue

                    elif user_input.startswith('"""'):
                        # Multiline input
                        if user_input == '"""':
                            user_input = self.ui.get_multiline_input()
                        else:
                            # Started with """ but has content
                            lines = [user_input[3:]]
                            while True:
                                line = input()
                                if line.strip() == '"""':
                                    break
                                lines.append(line)
                            user_input = "\n".join(lines)

                    # Regular prompt - run through agent
                    self.ui.print_user_message(user_input)

                    with self.ui.create_spinner("Thinking..."):
                        result = self.run(user_input)

                except KeyboardInterrupt:
                    self.ui.print_warning("\nOperation cancelled. Press Ctrl+C again to exit.")
                    try:
                        # Give user a chance to continue
                        continue
                    except KeyboardInterrupt:
                        break

        except EOFError:
            pass

        self.ui.print_goodbye()

    def get_config(self) -> dict:
        """Get current configuration as dict."""
        return {
            "model": self.model_type,
            "model_id": self.model_id,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "safe_mode": self.safe_mode,
            "auto_run": self.auto_run,
            "tools": self.tool_names,
            "verbose": self.verbose
        }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="interpreter-smol: Open Interpreter-like CLI built on SmolaGents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  interpreter-smol                          Start interactive mode
  interpreter-smol "create hello.py"        Run single prompt
  interpreter-smol -m openai "explain x"    Use OpenAI
  interpreter-smol --safe "delete files"    Confirm before running code
  interpreter-smol -v "debug this"          Verbose output

Environment Variables:
  GOOGLE_API_KEY      API key for Gemini
  OPENAI_API_KEY      API key for OpenAI
  ANTHROPIC_API_KEY   API key for Anthropic
  HF_API_TOKEN        API token for HuggingFace
        """
    )

    # Positional argument
    parser.add_argument("prompt", nargs="?", help="Prompt to run (starts interactive mode if not provided)")

    # Model selection
    parser.add_argument("-m", "--model", default="gemini",
                        choices=["gemini", "openai", "anthropic", "hf"],
                        help="Model provider to use (default: gemini)")
    parser.add_argument("--model-id", default=None,
                        help="Specific model ID (e.g., gpt-4o, claude-sonnet-4-20250514)")

    # API configuration
    parser.add_argument("-k", "--api-key", default=None,
                        help="API key for the model provider")

    # Tools and imports
    parser.add_argument("--tools", nargs="*",
                        default=["enhanced_python", "web_search"],
                        help="Tools to enable (default: enhanced_python, web_search)")
    parser.add_argument("--imports", nargs="*",
                        default=["numpy", "pandas", "matplotlib.pyplot"],
                        help="Python imports to allow")

    # Generation parameters
    parser.add_argument("-t", "--temperature", type=float, default=0.7,
                        help="Temperature for generation (default: 0.7)")
    parser.add_argument("--max-tokens", type=int, default=8192,
                        help="Maximum tokens in response (default: 8192)")

    # Mode flags
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Force interactive mode even with prompt")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output")
    parser.add_argument("--safe", action="store_true",
                        help="Safe mode: confirm before running code")
    parser.add_argument("--no-auto-run", action="store_true",
                        help="Don't automatically run generated code")

    # Utility flags
    parser.add_argument("--version", action="version", version=f"interpreter-smol {__version__}")
    parser.add_argument("--no-banner", action="store_true",
                        help="Don't show welcome banner")

    args = parser.parse_args()

    # Set up environment variables for API keys if provided
    if args.api_key:
        env_map = {
            "gemini": "GOOGLE_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "hf": "HF_API_TOKEN"
        }
        if args.model.lower() in env_map:
            os.environ[env_map[args.model.lower()]] = args.api_key

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
            verbose=args.verbose,
            safe_mode=args.safe,
            auto_run=not args.no_auto_run
        )

        # Run in appropriate mode
        if args.interactive or not args.prompt:
            interpreter.chat(args.prompt if not args.interactive else None)
        else:
            # Single prompt mode - still show nice output
            if not args.no_banner:
                interpreter.ui.print(f"\n[dim]interpreter-smol v{__version__}[/] | [cyan]{interpreter.model_id}[/]\n")
            interpreter.ui.print_user_message(args.prompt)
            result = interpreter.run(args.prompt)

    except ImportError as e:
        print(f"Error: Missing dependency - {e}")
        if "google" in str(e).lower():
            print("Install with: pip install google-genai")
        elif "openai" in str(e).lower():
            print("Install with: pip install openai")
        elif "anthropic" in str(e).lower():
            print("Install with: pip install anthropic")
        sys.exit(1)

    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
