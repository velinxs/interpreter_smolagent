# Migration Guide: Moving from Open-Interpreter to interpreter-smol

This guide helps Open-Interpreter users transition to interpreter-smol. The migration should be straightforward as interpreter-smol is designed to provide a similar experience while leveraging the more robust SmolAgents framework.

## Why Migrate?

- **Native Gemini 2.0 Support**: First-class integration with Google's latest Gemini models
- **More Robust Framework**: Built on SmolAgents, a well-maintained agent framework
- **Enhanced Security**: Better code execution isolation options
- **Active Development**: Regular updates and community support
- **Simple Implementation**: Focused on essential functionality

## CLI Command Changes

### Open-Interpreter

```bash
# Basic usage
interpreter "Generate a function to calculate prime numbers"

# With model
interpreter --model gpt-4

# With system message
interpreter --system "You are a helpful coding assistant"

# Auto-run
interpreter --auto-run

# Debug mode
interpreter --debug
```

### interpreter-smol

```bash
# Basic usage (very similar)
interpreter-smol "Generate a function to calculate prime numbers"

# With model (slightly different format)
interpreter-smol --model openai --model-id gpt-4o

# No direct system message, but can be achieved through custom prompts
# See advanced usage section below

# Interactive mode is default, just start:
interpreter-smol

# Verbose mode (similar to debug)
interpreter-smol -v
```

## Python API Changes

### Open-Interpreter

```python
from interpreter import interpreter

# Set model
interpreter.model = "gpt-4"

# Configuration
interpreter.auto_run = True
interpreter.debug = True

# Run interpreter
interpreter.chat("Write a function to calculate prime numbers")

# Run a single command
output = interpreter.run("Write a function to calculate prime numbers")
```

### interpreter-smol

```python
from interpreter_smol import Interpreter

# Initialize with configuration
interpreter = Interpreter(
    model="openai",
    model_id="gpt-4o",
    verbose=True  # Similar to debug
)

# Run interpreter
interpreter.chat("Write a function to calculate prime numbers")

# Run a single command
output = interpreter.run("Write a function to calculate prime numbers")
```

## Tool Mapping

| Open-Interpreter | interpreter-smol |
|------------------|------------------|
| Interpreter mode (default) | `python_interpreter` tool |
| N/A | `web_search` tool (built-in) |
| N/A | `visit_webpage` tool (built-in) |

## Environment Variables

### Open-Interpreter

```bash
# OpenAI
export OPENAI_API_KEY="your-api-key"

# Anthropic
export ANTHROPIC_API_KEY="your-api-key"

# Azure OpenAI
export AZURE_API_KEY="your-api-key"
export AZURE_API_BASE="your-api-base"
export AZURE_API_VERSION="your-api-version"
export AZURE_DEPLOYMENT_NAME="your-deployment-name"
```

### interpreter-smol

```bash
# Gemini (default in interpreter-smol)
export GOOGLE_API_KEY="your-api-key"

# OpenAI (same as Open-Interpreter)
export OPENAI_API_KEY="your-api-key"

# Anthropic (same as Open-Interpreter)
export ANTHROPIC_API_KEY="your-api-key"

# Hugging Face
export HF_API_TOKEN="your-api-key"
```

## Advanced Usage

### Custom System Prompt with interpreter-smol

While interpreter-smol doesn't have a direct `--system` flag, you can achieve similar results by customizing your prompt:

```python
from interpreter_smol import Interpreter

# Create a custom system-like preamble
system_instruction = """You are a Python expert specialized in data science.
Always explain your code before writing it, and provide clear comments.
"""

# Initialize the interpreter
interpreter = Interpreter(model="gemini")

# Add the system instruction at the beginning of your prompt
interpreter.run(f"{system_instruction}\n\nAnalyze this dataset and create visualizations.")
```

### Using SmolAgents Directly

For more advanced customization, you can use SmolAgents directly:

```python
from smolagents import CodeAgent
from smolagents.default_tools import TOOL_MAPPING
from gemini_model import GeminiModel

# Create model
model = GeminiModel(model_id="gemini-2.0-flash")

# Create agent with custom system prompt
agent = CodeAgent(
    tools=[TOOL_MAPPING["python_interpreter"]()],
    model=model,
    prompt_templates={
        "system_prompt": "You are a Python expert specialized in data science...",
        # Additional template customizations
    }
)

# Run the agent
agent.run("Analyze this dataset")
```

## Common Issues and Solutions

### Issue: Missing Gemini Support

**Error:**
```
ImportError: Google GenAI package not installed
```

**Solution:**
```bash
pip install google-genai
```

### Issue: Model Not Found

**Error:**
```
ValueError: Unable to find model with ID: gemini-xyz
```

**Solution:**
Check that you're using a valid model ID for the provider:
- Gemini: "gemini-2.0-flash", "gemini-2.0-pro"
- OpenAI: "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"
- Anthropic: "claude-3-5-sonnet-20240620", "claude-3-opus-20240229"

### Issue: Tool Not Available

**Error:**
```
Warning: Unknown tool 'x'. Available tools: python_interpreter, web_search, visit_webpage
```

**Solution:**
Check the available tools in SmolAgents or add custom tools:

```python
from smolagents.default_tools import TOOL_MAPPING
print(list(TOOL_MAPPING.keys()))
```

## Further Resources

- [SmolAgents Documentation](https://huggingface.co/docs/smolagents)
- [interpreter-smol GitHub Repository](https://github.com/your-username/interpreter-smol)
- [Google GenAI Documentation](https://ai.google.dev/docs)