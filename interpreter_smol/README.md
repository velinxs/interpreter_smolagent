# interpreter-smol

**Open Interpreter, but smol.** A beautiful, powerful AI code interpreter built on [smolagents](https://github.com/huggingface/smolagents).

```
  ___       _                          _
 |_ _|_ __ | |_ ___ _ __ _ __  _ __ ___| |_ ___ _ __
  | || '_ \| __/ _ \ '__| '_ \| '__/ _ \ __/ _ \ '__|
  | || | | | ||  __/ |  | |_) | | |  __/ ||  __/ |
 |___|_| |_|\__\___|_|  | .__/|_|  \___|\__\___|_|
                        |_|          smol edition
```

## Features

- **Beautiful CLI** - Rich terminal UI with syntax highlighting, panels, and spinners
- **Multi-Model Support** - Gemini, OpenAI, Anthropic, and HuggingFace
- **Code Execution** - Full Python execution with system access
- **Shell Integration** - Run shell commands with `!` prefix
- **Conversation History** - Save and load conversations
- **Safe Mode** - Optional confirmation before running code
- **Evolving Agents** - Create and manage persistent AI agents

## Quick Start

```bash
# Install
pip install -e .

# Run (interactive mode)
interpreter-smol

# Or use short aliases
smol
i

# Run with a prompt
interpreter-smol "create a hello world script"

# Use a different model
interpreter-smol -m openai "explain this code"
interpreter-smol -m anthropic "fix this bug"
```

## Installation

```bash
# Clone and install
git clone https://github.com/velinxs/interpreter_smolagent.git
cd interpreter_smolagent
pip install -e ".[complete]"

# Or just the basics
pip install -e .
```

Set up your API key:

```bash
# Gemini (default)
export GOOGLE_API_KEY=your_key

# Or OpenAI
export OPENAI_API_KEY=your_key

# Or Anthropic
export ANTHROPIC_API_KEY=your_key
```

## Usage

### Interactive Mode

```bash
interpreter-smol
```

This launches the beautiful interactive CLI:

```
> Create a Python script that finds prime numbers

[Code]
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

primes = [n for n in range(2, 100) if is_prime(n)]
print(f"Prime numbers: {primes}")

[Output]
Prime numbers: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
```

### Commands

Inside the interpreter:

| Command | Description |
|---------|-------------|
| `exit`, `quit`, `q` | Exit the interpreter |
| `!<command>` | Run shell command (e.g., `!ls -la`) |
| `?` | Show help |
| `clear` | Clear screen |
| `reset` | Reset conversation |
| `history` | Show conversation history |
| `save [file]` | Save conversation to file |
| `config` | Show current configuration |
| `"""` | Start multiline input |

### CLI Options

```bash
interpreter-smol [OPTIONS] [PROMPT]

Options:
  -m, --model         Model provider: gemini, openai, anthropic, hf (default: gemini)
  --model-id          Specific model ID (e.g., gpt-4o, claude-sonnet-4-20250514)
  -k, --api-key       API key for the provider
  -t, --temperature   Generation temperature (default: 0.7)
  --max-tokens        Max tokens in response (default: 8192)
  -v, --verbose       Enable verbose output
  --safe              Safe mode: confirm before running code
  -i, --interactive   Force interactive mode
  --tools             Tools to enable (default: enhanced_python, web_search)
  --version           Show version
```

### Examples

```bash
# Basic usage
interpreter-smol "what files are in the current directory?"

# Use OpenAI
interpreter-smol -m openai "explain how async works in Python"

# Verbose mode
interpreter-smol -v "debug this error"

# Safe mode (confirms before running code)
interpreter-smol --safe "delete all .tmp files"

# Different model
interpreter-smol --model-id gpt-4o "refactor this function"

# Interactive with initial prompt
interpreter-smol -i "let's build a web scraper"
```

## Python API

```python
from interpreter_smol import Interpreter

# Initialize
interpreter = Interpreter(
    model="gemini",           # or "openai", "anthropic", "hf"
    temperature=0.7,
    verbose=False,
    safe_mode=False
)

# Run a single prompt
result = interpreter.run("Calculate fibonacci sequence")

# Start interactive chat
interpreter.chat()

# Run with initial prompt and continue chatting
interpreter.chat("Let's build a web scraper")
```

## Evolving Agent System

Create persistent AI agents that can be reused:

```bash
# Launch evolving agent system
interpreter-evolve

# With custom workspace
interpreter-evolve -w ./my_agents
```

```python
from interpreter_smol.agents import EvolvingAgentSystem

system = EvolvingAgentSystem(workspace_dir="./agents")

# Create an agent
system.run("Create an agent called 'researcher' that searches the web and summarizes findings")

# Use the agent
system.run("researcher, find recent news about AI")

# List agents
system.run("List all agents")
```

## Available Tools

| Tool | Description |
|------|-------------|
| `enhanced_python` | Full system Python execution |
| `web_search` | DuckDuckGo web search |
| `visit_webpage` | Extract webpage content |

## Project Structure

```
interpreter_smol/
├── core/
│   ├── interpreter.py    # Main interpreter
│   └── ui.py             # Rich terminal UI
├── agents/
│   └── evolving_agent.py # Evolving agent system
├── tools/
│   └── enhanced_python.py # Python execution
└── prompts/
    └── code_agent.yaml    # System prompts
```

## Troubleshooting

**API Key Issues**
```bash
# Check your key is set
echo $GOOGLE_API_KEY
echo $OPENAI_API_KEY

# Or pass directly
interpreter-smol -k your_api_key "hello"
```

**Missing Dependencies**
```bash
# Install all dependencies
pip install -e ".[complete]"

# Or specific provider
pip install -e ".[openai]"
```

**Import Errors**
```bash
# Make sure you're in the right directory
cd interpreter_smolagent
pip install -e .
```

## Contributing

Contributions welcome! This project aims to be a simpler, more hackable alternative to Open Interpreter.

## License

MIT License

---

Built with [smolagents](https://github.com/huggingface/smolagents) and [Rich](https://github.com/Textualize/rich)
