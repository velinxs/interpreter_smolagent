# interpreter-smol: Installation and Usage Guide

This guide will help you set up and use `interpreter-smol`, a thin wrapper around SmolaGents that provides an Open-Interpreter-like experience with Gemini support.

## Installation

1. Install the required packages:

```bash
# Install SmolaGents and base requirements
pip install smolagents

# Install Gemini support (required for default model)
pip install google-genai
```

2. Download and install the interpreter-smol package:

```bash
# Clone the repository
git clone https://github.com/your-username/interpreter-smol.git
cd interpreter-smol

# Install the package
pip install -e .
```

3. Set up your API keys as environment variables:

```bash
# For Gemini (recommended)
export GOOGLE_API_KEY="your-api-key-here"

# For other providers (optional)
export OPENAI_API_KEY="your-api-key-here"
export ANTHROPIC_API_KEY="your-api-key-here"
export HF_API_TOKEN="your-api-key-here"
```

## Basic Usage

### Command Line Interface

The command line interface is designed to be simple and familiar to Open-Interpreter users:

```bash
# Basic usage (defaults to Gemini model)
interpreter-smol "Write a Python function to calculate the Fibonacci sequence"

# Start an interactive chat session
interpreter-smol

# Specify a different model provider
interpreter-smol --model openai "Write a function to calculate prime numbers"

# Enable specific tools
interpreter-smol --tools unrestricted_python web_search "Find the current Bitcoin price and plot it"

# Allow additional Python imports
interpreter-smol --imports numpy pandas matplotlib.pyplot scipy "Create a visualization of the sine function"

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
result = interpreter.run("Write a Python function to calculate prime numbers")

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

- `unrestricted_python`: Execute Python code
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

## Advanced Usage with SmolaGents

For more advanced use cases, you can access the SmolaGents functionality directly:

```python
from smolagents import CodeAgent
from smolagents import LiteLLMModel
from smolagents.default_tools import TOOL_MAPPING

# Create a custom Gemini model
model = LiteLLMModel(model_id="gemini/gemini-2.0-flash")

# Create an agent with specific tools
agent = CodeAgent(
    tools=[TOOL_MAPPING["unrestricted_python"](), TOOL_MAPPING["web_search"]()],
    model=model,
    additional_authorized_imports=["numpy", "pandas"],
    verbosity_level=2
)

# Run the agent
agent.run("Your complex task here")
```

## Differences from Open-Interpreter

interpreter-smol offers several advantages compared to Open-Interpreter:

1. **Native Gemini 2.0 support**: First-class integration with Google's latest Gemini models
2. **Modern agent framework**: Built on SmolaGents, providing a more robust foundation
3. **Enhanced security**: Better code execution security options
4. **Simplified implementation**: Thin wrapper focused on essential functionality
5. **Open-source foundation**: Built on the well-maintained SmolaGents library

## Limitations

- Some advanced features from Open-Interpreter (like vision) require additional setup
- Currently focused on core functionality; some specialized features may not be available yet