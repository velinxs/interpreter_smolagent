"""
Beautiful CLI UI components for interpreter-smol using Rich.
Provides Open Interpreter-like experience with syntax highlighting, panels, and more.
"""

import os
import sys
import platform
import time
from typing import Optional, Generator, Any
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.text import Text
    from rich.box import ROUNDED, HEAVY, DOUBLE
    from rich.style import Style
    from rich.theme import Theme
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.rule import Rule
    from rich.prompt import Prompt, Confirm
    from rich import print as rprint
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Custom theme for the interpreter
INTERPRETER_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "code": "bright_white on grey23",
    "user": "bold bright_blue",
    "assistant": "bold bright_green",
    "system": "dim",
    "highlight": "bold magenta",
})

# ASCII Art banner
BANNER = r"""
   ____ _                 _
  / ___| | __ _ _   _  __| | ___
 | |   | |/ _` | | | |/ _` |/ _ \
 | |___| | (_| | |_| | (_| |  __/
  \____|_|\__,_|\__,_|\__,_|\___|
  [bold cyan]interpreter[/]  [dim]powered by Claude Code[/]
"""

MINI_BANNER = "[bold bright_green]claude-interpreter[/] [dim]v0.4.0[/]"


class InterpreterUI:
    """Rich-powered UI for the interpreter."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        if HAS_RICH:
            self.console = Console(theme=INTERPRETER_THEME)
        else:
            self.console = None
        self.start_time = time.time()
        self.message_count = 0
        self._streaming = False

    def print(self, *args, **kwargs):
        """Print with Rich if available, else fallback to standard print."""
        if self.console:
            self.console.print(*args, **kwargs)
        else:
            print(*args, **kwargs)

    def print_assistant_start(self):
        """Mark the start of assistant response streaming."""
        self._streaming = True
        if not HAS_RICH:
            print("\n", end="", flush=True)
            return
        self.console.print()

    def print_stream(self, chunk: str):
        """Print a streaming text chunk (no newline added)."""
        if not HAS_RICH:
            print(chunk, end="", flush=True)
            return
        self.console.print(chunk, end="", highlight=False)

    def print_stream_end(self):
        """Mark end of streaming response."""
        self._streaming = False
        if not HAS_RICH:
            print(flush=True)
            return
        self.console.print()

    def print_banner(self, show_full: bool = True):
        """Display the interpreter banner."""
        if not HAS_RICH:
            print("\n=== interpreter-smol ===\n")
            return

        if show_full:
            self.console.print(BANNER, style="bright_green")
        else:
            self.console.print(f"\n{MINI_BANNER}\n")

    def print_system_info(self):
        """Display system information panel."""
        if not HAS_RICH:
            print(f"System: {platform.system()} | Python: {platform.python_version()}")
            return

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Key", style="dim")
        table.add_column("Value", style="cyan")

        table.add_row("OS", f"{platform.system()} {platform.release()}")
        table.add_row("Python", platform.python_version())
        table.add_row("Working Dir", os.getcwd())
        table.add_row("Time", datetime.now().strftime("%Y-%m-%d %H:%M"))

        panel = Panel(
            table,
            title="[bold]System Info[/]",
            border_style="dim",
            box=ROUNDED,
            padding=(0, 1)
        )
        self.console.print(panel)

    def print_welcome(self, model: str = "gemini", model_id: str = None):
        """Display welcome message with instructions."""
        self.print_banner(show_full=True)
        self.print_system_info()

        if not HAS_RICH:
            print(f"\nModel: {model_id or model}")
            print("\nCommands: 'exit' to quit, '!' for shell, '?' for help\n")
            return

        # Model info
        model_display = model_id or f"{model} (default)"
        self.console.print(f"\n[dim]Model:[/] [bold cyan]{model_display}[/]")

        # Quick help
        help_text = """
[dim]Commands:[/]
  [bold]exit[/], [bold]quit[/], [bold]q[/]  - Exit the interpreter
  [bold]!<cmd>[/]          - Run shell command (e.g., !ls -la)
  [bold]?[/]               - Show help
  [bold]clear[/]           - Clear screen
  [bold]reset[/]           - Reset conversation
  [bold]history[/]         - Show conversation history
  [bold]save[/]            - Save conversation to file

[dim]Tips:[/]
  • Use [bold]\"\"\"[/] for multiline input
  • Press [bold]Ctrl+C[/] to cancel current operation
  • Code executes automatically (use [bold]--safe[/] to confirm)
"""
        self.console.print(Panel(
            help_text,
            title="[bold]Quick Reference[/]",
            border_style="dim",
            box=ROUNDED
        ))
        self.console.print()

    def print_help(self):
        """Display detailed help."""
        if not HAS_RICH:
            print("""
Commands:
  exit, quit, q  - Exit the interpreter
  !<cmd>         - Run shell command
  ?              - Show this help
  clear          - Clear screen
  reset          - Reset conversation
  history        - Show conversation history
  save           - Save conversation to file
            """)
            return

        help_md = """
## Commands

| Command | Description |
|---------|-------------|
| `exit`, `quit`, `q` | Exit the interpreter |
| `!<command>` | Run a shell command directly |
| `?` | Show this help message |
| `clear` | Clear the screen |
| `reset` | Reset conversation history |
| `history` | Show conversation history |
| `save [file]` | Save conversation to file |
| `config` | Show current configuration |
| `model <name>` | Switch to a different model |

## Tips

- **Multiline Input**: Start with `\"\"\"` and end with `\"\"\"` on its own line
- **Shell Commands**: Prefix with `!` (e.g., `!pip install numpy`)
- **Safe Mode**: Use `--safe` flag to confirm before running code
- **Verbose Mode**: Use `-v` flag for detailed output

## Examples

```
> Create a file called hello.py with a simple hello world function

> !cat hello.py

> \"\"\"
Write a function that:
1. Takes a list of numbers
2. Returns the sum of squares
\"\"\"
```
"""
        self.console.print(Markdown(help_md))

    def print_user_message(self, message: str):
        """Display user input."""
        self.message_count += 1
        if not HAS_RICH:
            print(f"\n>>> {message}")
            return

        self.console.print(f"\n[user]>[/] {message}")

    def print_assistant_thinking(self, message: str = "Thinking..."):
        """Display thinking indicator."""
        if not HAS_RICH:
            print(f"... {message}")
            return
        self.console.print(f"[dim]{message}[/]")

    def print_code_block(self, code: str, language: str = "python", title: str = "Code"):
        """Display syntax-highlighted code block."""
        if not HAS_RICH:
            print(f"\n--- {title} ({language}) ---")
            print(code)
            print("---")
            return

        syntax = Syntax(
            code.strip(),
            language,
            theme="monokai",
            line_numbers=True,
            word_wrap=True
        )
        panel = Panel(
            syntax,
            title=f"[bold]{title}[/]",
            border_style="bright_blue",
            box=ROUNDED
        )
        self.console.print(panel)

    def print_output(self, output: str, title: str = "Output"):
        """Display command/code output."""
        if not output or not output.strip():
            return

        if not HAS_RICH:
            print(f"\n--- {title} ---")
            print(output)
            return

        # Check if output looks like an error
        is_error = any(x in output.lower() for x in ['error', 'exception', 'traceback'])
        style = "red" if is_error else "green"

        self.console.print(Panel(
            output.strip(),
            title=f"[bold]{title}[/]",
            border_style=style,
            box=ROUNDED
        ))

    def print_error(self, error: str, title: str = "Error"):
        """Display error message."""
        if not HAS_RICH:
            print(f"\n!!! {title}: {error}")
            return

        self.console.print(Panel(
            f"[red]{error}[/]",
            title=f"[bold red]{title}[/]",
            border_style="red",
            box=HEAVY
        ))

    def print_success(self, message: str):
        """Display success message."""
        if not HAS_RICH:
            print(f"✓ {message}")
            return
        self.console.print(f"[success]✓[/] {message}")

    def print_warning(self, message: str):
        """Display warning message."""
        if not HAS_RICH:
            print(f"⚠ {message}")
            return
        self.console.print(f"[warning]⚠[/] {message}")

    def print_info(self, message: str):
        """Display info message."""
        if not HAS_RICH:
            print(f"ℹ {message}")
            return
        self.console.print(f"[info]ℹ[/] {message}")

    def print_shell_command(self, command: str):
        """Display shell command being executed."""
        if not HAS_RICH:
            print(f"\n$ {command}")
            return
        self.console.print(f"\n[bold yellow]$[/] [code]{command}[/]")

    def print_shell_output(self, output: str, return_code: int = 0):
        """Display shell command output."""
        if not output:
            return

        if not HAS_RICH:
            print(output)
            if return_code != 0:
                print(f"(exit code: {return_code})")
            return

        style = "red" if return_code != 0 else "dim"
        self.console.print(f"[{style}]{output}[/]")
        if return_code != 0:
            self.console.print(f"[dim](exit code: {return_code})[/]")

    def print_markdown(self, text: str):
        """Display markdown formatted text."""
        if not HAS_RICH:
            print(text)
            return
        self.console.print(Markdown(text))

    def print_divider(self, title: str = ""):
        """Print a divider line."""
        if not HAS_RICH:
            print("-" * 50)
            return
        self.console.print(Rule(title, style="dim"))

    def print_conversation_history(self, history: list):
        """Display conversation history."""
        if not history:
            self.print_info("No conversation history yet.")
            return

        if not HAS_RICH:
            for i, msg in enumerate(history, 1):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:100]
                print(f"{i}. [{role}] {content}...")
            return

        table = Table(title="Conversation History", box=ROUNDED)
        table.add_column("#", style="dim", width=4)
        table.add_column("Role", style="cyan", width=10)
        table.add_column("Content", style="white")

        for i, msg in enumerate(history, 1):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            # Truncate long content
            if len(content) > 100:
                content = content[:100] + "..."
            table.add_row(str(i), role, content)

        self.console.print(table)

    def print_config(self, config: dict):
        """Display current configuration."""
        if not HAS_RICH:
            for k, v in config.items():
                print(f"  {k}: {v}")
            return

        table = Table(title="Current Configuration", box=ROUNDED)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")

        for key, value in config.items():
            table.add_row(key, str(value))

        self.console.print(table)

    def get_input(self, prompt: str = "> ") -> str:
        """Get user input with prompt."""
        if HAS_RICH:
            return self.console.input(f"[user]{prompt}[/]")
        return input(prompt)

    def get_multiline_input(self) -> str:
        """Get multiline input from user."""
        lines = []
        if HAS_RICH:
            self.console.print("[dim]Enter your message (end with \"\"\" on its own line):[/]")
        else:
            print("Enter your message (end with \"\"\" on its own line):")

        while True:
            try:
                line = input()
                if line.strip() == '"""':
                    break
                lines.append(line)
            except EOFError:
                break

        return "\n".join(lines)

    def confirm(self, message: str, default: bool = True) -> bool:
        """Ask for user confirmation."""
        if HAS_RICH:
            return Confirm.ask(message, default=default)
        response = input(f"{message} [{'Y/n' if default else 'y/N'}]: ").strip().lower()
        if not response:
            return default
        return response in ('y', 'yes')

    def clear(self):
        """Clear the screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def create_spinner(self, message: str = "Processing..."):
        """Create a spinner context manager."""
        if HAS_RICH:
            return self.console.status(f"[bold green]{message}[/]", spinner="dots")
        # Return a dummy context manager for non-Rich environments
        class DummySpinner:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def update(self, text): pass
        return DummySpinner()

    def print_step(self, step_num: int, total: int, description: str):
        """Print a step in a multi-step process."""
        if not HAS_RICH:
            print(f"[{step_num}/{total}] {description}")
            return
        self.console.print(f"[dim][{step_num}/{total}][/] {description}")

    def print_final_answer(self, answer: str):
        """Display the final answer prominently."""
        if not HAS_RICH:
            print(f"\n=== Result ===\n{answer}\n")
            return

        self.console.print()
        self.console.print(Panel(
            Markdown(answer) if '\n' in answer or '#' in answer else answer,
            title="[bold green]Result[/]",
            border_style="green",
            box=DOUBLE,
            padding=(1, 2)
        ))
        self.console.print()

    def print_stats(self):
        """Print session statistics."""
        elapsed = time.time() - self.start_time
        mins, secs = divmod(int(elapsed), 60)

        if not HAS_RICH:
            print(f"\nSession: {mins}m {secs}s | Messages: {self.message_count}")
            return

        self.console.print(f"\n[dim]Session: {mins}m {secs}s | Messages: {self.message_count}[/]")

    def print_goodbye(self):
        """Display goodbye message."""
        self.print_stats()
        if not HAS_RICH:
            print("\nGoodbye! 👋")
            return
        self.console.print("\n[bold bright_green]Goodbye![/] 👋\n")


# Callback handler for streaming agent output
class RichAgentCallback:
    """Callback handler for rich display of agent steps."""

    def __init__(self, ui: InterpreterUI):
        self.ui = ui
        self.current_step = 0

    def on_step_start(self, step: int, thought: str):
        """Called when agent starts a new step."""
        self.current_step = step
        if thought:
            self.ui.print(f"\n[dim]Step {step}:[/] [italic]{thought}[/]")

    def on_code_generated(self, code: str, language: str = "python"):
        """Called when agent generates code."""
        self.ui.print_code_block(code, language=language, title=f"Step {self.current_step} - Code")

    def on_code_executed(self, output: str, error: str = None):
        """Called when code execution completes."""
        if error:
            self.ui.print_error(error, title="Execution Error")
        elif output:
            self.ui.print_output(output, title="Output")

    def on_tool_call(self, tool_name: str, args: dict):
        """Called when agent calls a tool."""
        self.ui.print(f"[dim]Using tool:[/] [bold]{tool_name}[/]")

    def on_final_answer(self, answer: str):
        """Called when agent produces final answer."""
        self.ui.print_final_answer(answer)
