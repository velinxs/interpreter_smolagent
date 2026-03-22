# claude-interpreter

Open Interpreter-like REPL powered by Claude Code.

Send prompts, Claude writes Python, we execute it. No tool calls, no overhead — just code.

## Install

```bash
# Requires claude CLI
npm install -g @anthropic-ai/claude-code

# Install claude-interpreter
pip install -e .
```

## Usage

```bash
# Interactive REPL
claude-interpreter

# Short alias
ci

# Single prompt
ci "list all python files in this directory"

# Use Opus
ci -m opus "refactor this code"

# Continue last session for this directory
ci -c

# Safe mode (confirm before running code)
ci --safe

# Verbose (show cost + timing)
ci -v "analyze data.csv"
```

## How it works

1. You type a prompt
2. Sent to Claude via `claude -p` (print mode, no built-in tools)
3. Claude responds with Python code blocks
4. Code is executed locally with full system access
5. Output is fed back to Claude for the next turn

State persists across code blocks. Sessions are saved per-directory — use `-c` to resume.

## REPL Commands

| Command | Description |
|---------|-------------|
| `exit` / `q` | Quit |
| `!<cmd>` | Run shell command |
| `?` | Help |
| `clear` | Clear screen |
| `reset` | Reset session |
| `cost` | Show total cost |
| `"""` | Multiline input |

## Architecture

```
claude_interpreter/
  core/
    interpreter.py   # REPL + claude -p integration + session persistence
    executor.py      # Python code execution with stdout capture
    ui.py            # Rich terminal UI
```

Only dependency: `rich` (for the terminal UI). Everything else is Claude Code.

## Session Persistence

Sessions are saved per working directory (`~/.claude_interpreter/`). Use `ci -c` to
continue where you left off. `reset` in the REPL clears the saved session.
