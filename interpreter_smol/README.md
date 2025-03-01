# 🤖 interpreter-smol

A lightweight, powerful interpreter built on top of [smolagents](https://github.com/huggingface/smolagents). Think of it as a smarter, more flexible version of the original Open Interpreter!

## ✨ Key Features

- 🌟 **Enhanced Python Execution**: Full system access with safety when you need it
- 🤝 **Multiple Model Support**: Works with Gemini, OpenAI, Anthropic, and Hugging Face models
- 🧬 **Evolving Agent System**: Create and manage AI agents that can learn and adapt
- 🔧 **Extensible Tools**: Easy to add new capabilities through the tools system

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/interpreter-smol.git
cd interpreter-smol

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Quick Start

### Basic Usage

```python
from interpreter_smol import Interpreter

# Initialize with Gemini (default)
interpreter = Interpreter()

# Or choose your preferred model
interpreter = Interpreter(
    model="openai",
    model_id="gpt-4",  # optional - will use best model by default
    api_key="your-api-key"  # or set via environment variable
)

# Run a single command
interpreter.run("Calculate the first 10 prime numbers")

# Start interactive chat
interpreter.chat()
```

### Command Line Interface

```bash
# Interactive mode with Gemini
python -m interpreter_smol.cli -i

# Use a specific model
python -m interpreter_smol.cli -i --model openai --api-key your-api-key

# Run a single command
python -m interpreter_smol.cli "Create a simple web server in Python"
```

## 🔑 API Keys Setup

Set up your API keys as environment variables:

```bash
# For Gemini (default)
export GOOGLE_API_KEY=your_api_key_here

# For OpenAI
export OPENAI_API_KEY=your_api_key_here

# For Anthropic
export ANTHROPIC_API_KEY=your_api_key_here

# For Hugging Face
export HF_API_TOKEN=your_api_key_here
```

## 🛠️ Core Components

### Enhanced Python Interpreter

Our EnhancedPythonInterpreter provides unrestricted system access with helpful utilities:

```python
from interpreter_smol import Interpreter

interpreter = Interpreter(tools=["enhanced_python"])

# Full system access
interpreter.run("""
import os
print("Current directory:", os.getcwd())

# Use helper functions
result = run_shell("ls -la")
print(result)

# Easy file operations
write_file("test.txt", "Hello World!")
content = read_file("test.txt")
""")
```

### Evolving Agent System

Create and manage AI agents that can learn and adapt:

```python
from interpreter_smol.agents import EvolvingAgentSystem

# Initialize the system
system = EvolvingAgentSystem(
    model_type="gemini",
    workspace_dir="./agent_workspace"
)

# Create a new agent
system.interpreter.run("""
Create an agent that can:
1. Search the web
2. Process CSV files
3. Generate charts
Name it 'data_analyst'
""")

# Use the agent
system.interpreter.run("data_analyst, analyze sales.csv and create a trend chart")
```

See [EVOLVE.md](EVOLVE.md) for more details on the Evolving Agent System.

## 📁 Project Structure

```
interpreter_smol/
├── agents/               # Agent implementations
│   ├── evolving_agent.py # Self-evolving agent system
│   └── vision_browser.py # Vision-capable web browser
├── core/                # Core functionality
│   ├── interpreter.py   # Main interpreter class
│   └── models/         # Model integrations
├── tools/               # Tool implementations
│   ├── enhanced_python.py # Enhanced Python interpreter
│   └── local_python_executor_unrestricted.py # Unrestricted executor
├── prompts/             # System prompts
│   ├── code_agent.yaml  # CodeAgent prompt template
│   └── evolving_agent.yaml # Evolving agent prompt
└── examples/            # Usage examples
```

## 🎮 Available Tools

- **enhanced_python**: Full system access Python interpreter
- **web_search**: DuckDuckGo web search capability
- **visit_webpage**: Web page content extraction
- More tools can be added through the smolagents integration!

## 🎯 Examples

### Different Models

```python
# Gemini
interpreter = Interpreter(model="gemini")

# OpenAI (GPT-4)
interpreter = Interpreter(
    model="openai",
    model_id="gpt-4"
)

# Anthropic (Claude)
interpreter = Interpreter(
    model="anthropic",
    model_id="claude-3-sonnet"
)

# Hugging Face (e.g., Mixtral)
interpreter = Interpreter(
    model="hf",
    model_id="mistralai/Mixtral-8x7B-Instruct-v0.1"
)
```

### Custom Tools

```python
from smolagents import tool

@tool
def custom_tool(param1: str, param2: int) -> str:
    """Your tool description here."""
    # Tool implementation
    return f"Processed {param1} {param2} times"

# Add to interpreter
interpreter = Interpreter(tools=["enhanced_python", custom_tool])
```

## 🔧 Troubleshooting

1. **API Key Issues**
   - Check that your API keys are set correctly
   - Try running with `verbose=True` for more details

2. **Import Errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - For Gemini: `pip install google-genai`

3. **Permission Issues**
   - enhanced_python requires appropriate system permissions
   - Try running with restricted tools if needed

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

[MIT License](LICENSE)

---

**Note**: This project is built on top of smolagents and aims to provide a simpler, more flexible alternative to Open Interpreter. While we provide full system access through the enhanced_python tool, please use it responsibly!