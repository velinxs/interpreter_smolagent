# SmoLAgents Verified Guide

This guide contains only features directly verified from the SmoLAgents source code.

## Core Components

### 1. Built-in Tools
Verified from `default_tools.py`:
```python
# Available built-in tools:
- PythonInterpreterTool  # Evaluates Python code
- FinalAnswerTool       # Provides final answer
- UserInputTool        # Gets user input
- DuckDuckGoSearchTool # Web search using DuckDuckGo
- GoogleSearchTool     # Web search using Google (requires API key)
- VisitWebpageTool    # Reads webpage content
- SpeechToTextTool    # Audio transcription
```

### 2. CLI Support
Verified from `cli.py`:
```bash
# Basic command structure
smolagent "your prompt" --model-type "HfApiModel" --model-id "model_name" --tools "web_search"

# Default values
--model-type: "HfApiModel"
--model-id: "Qwen/Qwen2.5-Coder-32B-Instruct"
--tools: ["web_search"]
```

### 3. Tool Creation
Verified from `tools.py`:
```python
from smolagents import tool

@tool
def my_tool(param: str) -> str:
    """Tool description - MUST include Args and Returns sections
    
    Args:
        param: Parameter description
    
    Returns:
        str: Return value description
    """
    return f"Result: {param}"
```

### 4. Model Types
Verified from `models.py`:
```python
# Available model types:
- HfApiModel           # Hugging Face models
- OpenAIServerModel    # OpenAI-compatible endpoints
- LiteLLMModel        # LiteLLM integration
- TransformersModel   # Local transformers models
```

## Verified Example: Using Gemini with SmoLAgents

```python
import os
from smolagents import OpenAIServerModel, CodeAgent, DuckDuckGoSearchTool

# Initialize Gemini model through OpenAI-compatible endpoint
model = OpenAIServerModel(
    model_id="gemini-2.0-flash",
    api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.environ["GEMINI_API_KEY"]
)

# Create agent with a built-in tool
agent = CodeAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model
)

# Run a query
result = agent.run("Search for the current population of Tokyo")
print(result)
```

## Tool Requirements

Every tool must have:
1. Name (str)
2. Description (str)
3. Inputs (dict with types and descriptions)
4. Output type (str)
5. Forward method implementation

Example structure:
```python
from smolagents import Tool

class MyTool(Tool):
    name = "my_tool"
    description = "What the tool does"
    inputs = {
        "param": {
            "type": "string",
            "description": "Parameter description"
        }
    }
    output_type = "string"

    def forward(self, param: str) -> str:
        return f"Result: {param}"
```

## Authorized Types
Verified from source:
```python
AUTHORIZED_TYPES = [
    "string",
    "boolean",
    "integer",
    "number",
    "image",
    "audio",
    "array",
    "object",
    "any",
    "null"
]
```

## Important Notes

1. Security:
   - Tool code is executed in your environment
   - Always validate tool source before using
   - Check tool permissions and capabilities

2. Documentation:
   - All tools must have complete docstrings
   - Parameter types must match authorized types
   - Input/output types must be explicitly defined

3. Limitations:
   - Tools run in local environment by default
   - API keys needed for certain services
   - Network access required for web-based tools