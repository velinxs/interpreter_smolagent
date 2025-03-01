# interpreter-smol

A lightweight wrapper around SmoLAgents that provides an Open-Interpreter-like experience.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/interpreter-smol.git
cd interpreter-smol

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Setting Up API Keys

Before using interpreter-smol, you need to set up your API keys:

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

### Basic Usage

```python
from interpreter_smol import Interpreter

# Initialize with default settings (Gemini model)
interpreter = Interpreter()

# Run a simple prompt
result = interpreter.run("Calculate the first 10 prime numbers and print them")
print(result)
```

### Interactive Mode

```bash
# Start interactive mode with default settings
python -m interpreter_smol.cli -i

# Start with specific model
python -m interpreter_smol.cli -i --model openai
```

### Command Line Options

```bash
python -m interpreter_smol.cli --help
```

## Enhanced Python Interpreter

interpreter-smol includes an EnhancedPythonInterpreter that provides full system access:

```python
from interpreter_smol import Interpreter

# Initialize with enhanced Python interpreter
interpreter = Interpreter(tools=["enhanced_python"])

# Run Python code with full system access
interpreter.run("""
import os
print("Current directory:", os.getcwd())
with open('test.txt', 'w') as f:
    f.write('Hello from interpreter-smol!')
print("File created:", os.path.exists('test.txt'))
""")
```

## Evolving Agent System

For a more advanced experience, try the Evolving Agent System:

```bash
# Start the evolving agent system in interactive mode
python evolve.py
```

See [EVOLVE.md](EVOLVE.md) for more details on the Evolving Agent System.

## Troubleshooting

If you encounter issues:

1. Make sure your API keys are set correctly
2. Check that you have the required dependencies installed
3. Try running with the verbose flag: `python -m interpreter_smol.cli -v`

## License

[MIT License](LICENSE)