"""
interpreter-smol — Open Interpreter-like REPL powered by Claude Code print mode.

User types a prompt → sent to `claude -p` → response streamed with Rich UI →
Python code blocks auto-executed → output fed back to Claude on next turn.
"""

import json
import os
import re
import subprocess
import sys
import argparse
from pathlib import Path
from typing import Optional, List, Tuple

from claude_interpreter.core.ui import InterpreterUI, HAS_RICH
from claude_interpreter.core.executor import CodeExecutor

# Session persistence directory
SESSION_DIR = Path.home() / ".claude_interpreter"

__version__ = "0.4.0"

DEFAULT_SYSTEM_PROMPT = """\
You are an AI assistant running inside an interactive Python REPL.
When you need to perform actions, write Python code in fenced ```python blocks.
The code will be executed automatically and you will see the output.

Rules:
- Use Python code blocks for ALL actions: file I/O, shell commands (via subprocess), \
data analysis, web requests, etc.
- You have full system access. os, subprocess, requests, etc. are all available.
- State persists between code blocks within a session.
- Be concise. Write working code, not explanations of code.
- When the user asks you to do something, DO it with code, don't just explain how.
- For shell commands, use subprocess.run().
- Print results so the user can see them.
"""

# Regex to find fenced code blocks: ```python ... ``` or ```py ... ```
CODE_BLOCK_RE = re.compile(
    r"```(?:python|py)\s*\n(.*?)```", re.DOTALL
)


def parse_code_blocks(text: str) -> List[str]:
    """Extract Python code blocks from markdown-formatted text."""
    return CODE_BLOCK_RE.findall(text)


class Interpreter:
    """
    REPL that sends prompts to Claude Code print mode and auto-executes
    Python code blocks from the response.
    """

    def __init__(
        self,
        model: str = "sonnet",
        auto_run: bool = True,
        safe_mode: bool = False,
        verbose: bool = False,
        system_prompt: Optional[str] = None,
        allowed_tools: Optional[List[str]] = None,
        permission_mode: str = "default",
    ):
        self.model = model
        self.auto_run = auto_run
        self.safe_mode = safe_mode
        self.verbose = verbose
        self.system_prompt = system_prompt
        self.allowed_tools = allowed_tools
        self.permission_mode = permission_mode

        self.session_id: Optional[str] = None
        self.turn_count = 0
        self.total_cost = 0.0

        self.ui = InterpreterUI(verbose=verbose)
        self.executor = CodeExecutor()

    # ── Session persistence ─────────────────────────────────────────

    def _session_file(self) -> Path:
        """Session file scoped to current working directory."""
        cwd_hash = str(hash(os.getcwd())).replace("-", "n")
        return SESSION_DIR / f"session_{cwd_hash}.json"

    def save_session(self):
        """Save current session ID to disk for --continue."""
        if not self.session_id:
            return
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "session_id": self.session_id,
            "cwd": os.getcwd(),
            "model": self.model,
            "turn_count": self.turn_count,
            "total_cost": self.total_cost,
        }
        self._session_file().write_text(json.dumps(data))

    def load_session(self) -> bool:
        """Load previous session for current directory. Returns True if loaded."""
        sf = self._session_file()
        if not sf.exists():
            return False
        try:
            data = json.loads(sf.read_text())
            self.session_id = data["session_id"]
            self.turn_count = data.get("turn_count", 0)
            self.total_cost = data.get("total_cost", 0.0)
            return True
        except (json.JSONDecodeError, KeyError):
            return False

    # ── Claude CLI interaction ──────────────────────────────────────

    def _build_cmd(self, prompt: str) -> List[str]:
        """Build the claude CLI command."""
        cmd = [
            "claude", "-p",
            "--output-format", "stream-json",
            "--verbose",
        ]

        cmd += ["--model", self.model]

        # Disable all built-in tools — we execute code ourselves
        cmd += ["--tools", ""]

        # System prompt: tell Claude to output Python code blocks
        sys_prompt = self.system_prompt or DEFAULT_SYSTEM_PROMPT
        cmd += ["--system-prompt", sys_prompt]

        if self.session_id:
            cmd += ["--resume", self.session_id]

        if self.permission_mode != "default":
            cmd += ["--permission-mode", self.permission_mode]

        cmd.append(prompt)
        return cmd

    def _call_claude(self, prompt: str) -> Tuple[str, Optional[str]]:
        """
        Call claude -p and stream the response.
        Returns (full_response_text, session_id).
        """
        cmd = self._build_cmd(prompt)

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except FileNotFoundError:
            self.ui.print_error("'claude' CLI not found. Install with: npm install -g @anthropic-ai/claude-code")
            return "", None

        full_text = ""
        printed_len = 0  # Track how much we've already printed (stream sends cumulative text)
        session_id = None

        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            etype = event.get("type")

            if etype == "assistant":
                msg = event.get("message", {})
                for block in msg.get("content", []):
                    if block.get("type") == "text":
                        text = block.get("text", "")
                        # Only print the NEW portion (stream events contain full accumulated text)
                        if len(text) > printed_len:
                            delta = text[printed_len:]
                            self.ui.print_stream(delta)
                            printed_len = len(text)
                        full_text = text

            elif etype == "result":
                session_id = event.get("session_id")
                full_text = event.get("result", full_text)
                cost = event.get("total_cost_usd", 0)
                self.total_cost += cost
                if self.verbose:
                    duration = event.get("duration_ms", 0)
                    self.ui.print_info(f"  cost: ${cost:.4f}  time: {duration}ms")

        proc.wait()

        if proc.returncode != 0:
            stderr = proc.stderr.read()
            if stderr:
                self.ui.print_error(stderr.strip())

        return full_text, session_id

    # ── Code execution ──────────────────────────────────────────────

    def _execute_code_blocks(self, text: str) -> Optional[str]:
        """Parse and execute Python code blocks. Returns combined output or None."""
        blocks = parse_code_blocks(text)
        if not blocks:
            return None

        outputs = []
        for i, code in enumerate(blocks, 1):
            if self.safe_mode and not self.ui.confirm(f"Execute code block {i}?"):
                outputs.append(f"[block {i} skipped by user]")
                continue

            self.ui.print_code_block(code, title=f"Executing block {i}/{len(blocks)}")
            stdout, stderr = self.executor.run(code)

            if stdout:
                self.ui.print_output(stdout)
                outputs.append(stdout.rstrip())
            if stderr:
                self.ui.print_error(stderr, title="Execution Error")
                outputs.append(f"ERROR:\n{stderr.rstrip()}")

            if not stdout and not stderr:
                outputs.append("[no output]")

        return "\n".join(outputs) if outputs else None

    # ── Main loop ───────────────────────────────────────────────────

    def run(self, prompt: str) -> str:
        """Single-turn: send prompt, get response, execute code, return text."""
        self.turn_count += 1
        self.ui.print_assistant_start()
        response, sid = self._call_claude(prompt)
        self.ui.print_stream_end()

        if sid:
            self.session_id = sid
            self.save_session()

        if self.auto_run and response:
            output = self._execute_code_blocks(response)
            if output:
                # Feed execution results back to Claude
                feedback = f"Code execution output:\n```\n{output}\n```"
                self.ui.print_assistant_start()
                followup, sid2 = self._call_claude(feedback)
                self.ui.print_stream_end()
                if sid2:
                    self.session_id = sid2
                    self.save_session()
                return followup or response

        return response

    def chat(self, initial_prompt: Optional[str] = None):
        """Interactive REPL loop."""
        self.ui.print_welcome(model=self.model, model_id=self.model)

        if initial_prompt:
            self.ui.print_user_message(initial_prompt)
            self.run(initial_prompt)

        try:
            while True:
                try:
                    user_input = self.ui.get_input("\n> ").strip()

                    if not user_input:
                        continue

                    # Special commands
                    if user_input.lower() in ("exit", "quit", "q"):
                        break
                    elif user_input == "?":
                        self.ui.print_help()
                        continue
                    elif user_input.lower() == "clear":
                        self.ui.clear()
                        continue
                    elif user_input.lower() == "reset":
                        self.session_id = None
                        self.turn_count = 0
                        self.total_cost = 0.0
                        self.executor = CodeExecutor()
                        sf = self._session_file()
                        if sf.exists():
                            sf.unlink()
                        self.ui.print_success("Session reset!")
                        continue
                    elif user_input.lower() == "cost":
                        self.ui.print_info(f"Total cost: ${self.total_cost:.4f} | Turns: {self.turn_count}")
                        continue
                    elif user_input.lower() == "shell":
                        # Drop into interactive subshell — safe, no user-controlled args
                        shell = os.environ.get("SHELL", "/bin/bash")
                        self.ui.print_info(f"Dropping to {shell}. Type 'exit' to return.")
                        subprocess.run([shell])
                        self.ui.print_info("Back in interpreter.")
                        continue
                    elif user_input.startswith("!"):
                        cmd = user_input[1:].strip()
                        if cmd:
                            self._run_shell(cmd)
                        continue
                    elif user_input.startswith('"""'):
                        user_input = self._read_multiline(user_input)

                    self.run(user_input)

                except KeyboardInterrupt:
                    self.ui.print_warning("\nInterrupted. Press Ctrl+C again to exit.")
                    try:
                        continue
                    except KeyboardInterrupt:
                        break

        except EOFError:
            pass

        self.ui.print_goodbye()

    def _run_shell(self, command: str):
        """Run a shell command directly."""
        self.ui.print_shell_command(command)
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=300
            )
            output = result.stdout + result.stderr
            self.ui.print_shell_output(output, result.returncode)
        except subprocess.TimeoutExpired:
            self.ui.print_error("Command timed out after 5 minutes")

    def _read_multiline(self, first_line: str) -> str:
        """Read multiline input delimited by triple quotes."""
        lines = []
        if first_line != '"""':
            lines.append(first_line[3:])
        while True:
            try:
                line = input()
                if line.strip() == '"""':
                    break
                lines.append(line)
            except EOFError:
                break
        return "\n".join(lines)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="interpreter-smol: Open Interpreter-like REPL powered by Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  interpreter-smol                          Interactive REPL
  interpreter-smol "list files in ~/code"   Single prompt
  interpreter-smol -m opus "refactor x"     Use Opus model
  interpreter-smol --safe "delete tmp"      Confirm before executing code

Environment:
  Requires 'claude' CLI installed (npm install -g @anthropic-ai/claude-code)
        """,
    )

    parser.add_argument("prompt", nargs="?", help="Prompt (starts REPL if omitted)")
    parser.add_argument("-m", "--model", default="sonnet", help="Claude model (sonnet, opus, haiku)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output (show cost, timing)")
    parser.add_argument("--safe", action="store_true", help="Confirm before executing code blocks")
    parser.add_argument("--no-auto-run", action="store_true", help="Don't auto-execute code blocks")
    parser.add_argument("--system-prompt", default=None, help="Custom system prompt")
    parser.add_argument("--permission-mode", default="default",
                        choices=["default", "plan", "auto", "bypassPermissions"],
                        help="Claude permission mode")
    parser.add_argument("-c", "--continue-session", action="store_true",
                        dest="continue_session",
                        help="Continue the last session for this directory")
    parser.add_argument("-i", "--interactive", action="store_true", help="Force interactive mode")
    parser.add_argument("--version", action="version", version=f"interpreter-smol {__version__}")

    args = parser.parse_args()

    interpreter = Interpreter(
        model=args.model,
        auto_run=not args.no_auto_run,
        safe_mode=args.safe,
        verbose=args.verbose,
        system_prompt=args.system_prompt,
        permission_mode=args.permission_mode,
    )

    if args.continue_session:
        if interpreter.load_session():
            interpreter.ui.print_info(
                f"Resumed session (turns: {interpreter.turn_count}, "
                f"cost: ${interpreter.total_cost:.4f})"
            )
        else:
            interpreter.ui.print_warning("No previous session found for this directory.")

    if args.interactive or not args.prompt:
        interpreter.chat(args.prompt if not args.interactive else None)
    else:
        result = interpreter.run(args.prompt)


if __name__ == "__main__":
    main()
