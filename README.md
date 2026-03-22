# interpreter-smol: Installation and Usage Guide

This guide will help you set up and use `interpreter-smol`, a thin wrapper around SmolAgents that provides an Open-Interpreter-like experience with Gemini support.

## Quick Start

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate    # On Windows

# Install the package (includes support for Gemini, OpenAI, Anthropic, and OpenRouter via LiteLLM)
pip install -e .

# Run the interpreter
interpreter-smol          # Basic interpreter
# or
interpreter-evolve        # Evolving agent version powered by smolagents
```

## Installation Options

1. Basic Installation:

   ```bash
   # Clone the repository
   git clone https://github.com/your-username/interpreter-smol.git
   cd interpreter-smol

   # Install with basic dependencies
   pip install -e .
   ```

2. Additional Features:

   ```bash
   # For Hugging Face models:
   pip install -e .[hf]

   # For all features including data science tools:
   pip install -e .[complete]
   ```

3. Set up your API keys:

   ```bash
   # Set up your API keys as environment variables:
   export GOOGLE_API_KEY="your-api-key-here"      # For Gemini
   export OPENAI_API_KEY="your-api-key-here"      # For OpenAI
   export ANTHROPIC_API_KEY="your-api-key-here"   # For Anthropic
   export OPENROUTER_API_KEY="your-api-key-here"  # For OpenRouter
   export HF_API_TOKEN="your-api-key-here"        # For Hugging Face
   ```

## Basic Usage

### Command Line Interface

The command line interface is designed to be simple and familiar to Open-Interpreter users:

```bash
# Basic usage (defaults to Gemini model)
interpreter-smol "What are the 6th through 8th Fibonacci numbers?"

# Start an interactive chat session
interpreter-smol

# Specify a different model provider
interpreter-smol --model openai "Find the 619th prime number"

# Enable specific tools
interpreter-smol --tools unrestricted_python web_search "Find the current Bitcoin price and plot it"

# Allow additional Python imports
interpreter-smol --imports scipy "Create a visualization of the sine function"

# Enable verbose output
interpreter-smol -v "Calculate the factorial of 10"
```

### Python API

You can also use the interpreter programmatically in your Python code:

```python
from interpreter_smol import Interpreter

# Initialize with default settings (Gemini)
interpreter = Interpreter()

# Run a single prompt
result = interpreter.run("Count the number of words in this sentence.")

# Start an interactive chat session
interpreter.chat("Help me analyze this dataset")

# Customize model and tools
custom_interpreter = Interpreter(
    model="anthropic",
    model_id="claude-3-5-sonnet-20240620",
    tools=["unrestricted_python", "web_search", "visit_webpage"],
    imports=["numpy", "pandas", "scipy", "matplotlib.pyplot"],
    verbose=True
)
custom_interpreter.run("Analyze recent stock market trends")
```

## Available Tools

The following tools are available:

- `unrestricted_python`: Execute Python code with full system access
- `web_search`: Search the web with DuckDuckGo
- `visit_webpage`: Visit and extract content from a webpage

## Supported Models

- **Gemini** (default): Google's Gemini 2.0 models
- **OpenAI**: GPT-3.5, GPT-4 models
- **Anthropic**: Claude models
- **Hugging Face**: Models hosted on Hugging Face

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `--model`, `-m` | Model provider | `gemini` |
| `--model-id` | Specific model identifier | Depends on provider |
| `--api-key`, `-k` | API key | Uses environment variable |
| `--tools` | Tools to enable | `unrestricted_python`, `web_search` |
| `--imports` | Additional Python modules to allow | `numpy`, `pandas`, `matplotlib.pyplot` |
| `--temperature`, `-t` | Temperature for generation | `0.7` |
| `--max-tokens` | Maximum tokens in response | `4096` |
| `-i`, `--interactive` | Start in interactive mode | `False` |
| `-v`, `--verbose` | Enable verbose output | `False` |

## Advanced Usage with SmolAgents

For more advanced use cases, you can access the SmolAgents functionality directly:

```python
from smolagents import CodeAgent, LiteLLMModel
from smolagents.default_tools import TOOL_MAPPING
from interpreter_smol.tools import UnrestrictedPythonInterpreter

# Create a custom Gemini model
model = LiteLLMModel(model_id="gemini/gemini-2.0-flash")

# Create an agent with our unrestricted Python interpreter
agent = CodeAgent(
    tools=[UnrestrictedPythonInterpreter(), TOOL_MAPPING["web_search"]()],
    model=model,
    verbosity_level=2
)

# Run the agent
agent.run("Your complex task here")
```
