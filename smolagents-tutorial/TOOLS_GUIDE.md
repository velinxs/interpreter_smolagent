# SmoLAgents Tools Guide

## Ways to Access Tools

1. **Hub Tools**
```python
from smolagents import Tool

# Load a single tool
tool = Tool.from_hub("username/toolname")

# Load a collection of tools
from smolagents import ToolCollection
tools = ToolCollection.from_hub("huggingface-tools/collection-name")
```

2. **CLI Tools**
```bash
# General purpose agent
smolagent "Your task here" --model-type "HfApiModel" --tools "web_search"

# Web browsing agent
webagent "Browse xyz.com" --model-type "LiteLLMModel" --model-id "gemini-2.0-flash"
```

3. **Custom Tools**
```python
from smolagents import tool

@tool
def my_tool(param: str) -> str:
    """Tool description
    
    Args:
        param: Parameter description
    
    Returns:
        str: Return value description
    """
    return f"Processed {param}"
```

4. **LangChain Tools**
```python
from smolagents import Tool
from langchain.tools import BaseTool

langchain_tool = BaseTool(...)
smol_tool = Tool.from_langchain(langchain_tool)
```

5. **Hugging Face Space as Tool**
```python
tool = Tool.from_space("username/space-name")
```

## Creating Shareable Tools

1. **Basic Tool Structure**
```python
from smolagents import Tool

class MyTool(Tool):
    name = "my-tool"
    description = "What the tool does"
    inputs = {
        "param1": {"type": "string", "description": "Parameter description"}
    }
    output_type = "string"

    def forward(self, param1: str) -> str:
        return f"Processed {param1}"
```

2. **Sharing to Hub**
```python
tool.push_to_hub(
    repo_id="username/toolname",
    commit_message="Added new tool",
    private=False
)
```

3. **Tool Collections**
```python
from smolagents import ToolCollection

# Create collection
collection = ToolCollection([tool1, tool2, tool3])

# Share collection
collection.push_to_hub("username/collection-name")
```

## Evolving Tools System

1. **Base Components**
- Tool search and discovery
- Dynamic tool loading
- Tool creation and validation
- Tool sharing and versioning

2. **Implementation Approaches**
- Use Hub API for tool discovery
- Implement tool validation
- Add monitoring and metrics
- Create feedback loops

3. **Best Practices**
- Always validate loaded tools
- Use proper error handling
- Implement security checks
- Document tool interactions

4. **Security Considerations**
- Trust levels for tools
- Code execution sandboxing
- Input validation
- Output sanitization

## CLI Integration

1. **Custom CLI Commands**
```python
def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("task")
    parser.add_argument("--tools", nargs="+")
    args = parser.parse_args()
    
    agent = setup_agent(args.tools)
    result = agent.run(args.task)
    print(result)
```

2. **Tool Discovery**
```bash
# List available tools
smolagent list-tools

# Search for tools
smolagent search-tools "image generation"

# Install tool
smolagent install-tool "username/toolname"
```

## Example: Self-Evolving Tool System

The example in `evolving_tools.py` demonstrates:
1. Dynamic tool discovery
2. Automatic tool loading
3. Tool creation when needed
4. Continuous learning and adaptation

Key features:
- Searches Hub for relevant tools
- Loads tools dynamically
- Creates new tools when needed
- Maintains tool state
- Provides feedback loop

Usage:
```python
agent = EvolvingToolAgent(model)
result = agent.run("Your task here")
```

## Resources

1. [SmoLAgents Documentation](https://huggingface.co/docs/smolagents/index)
2. [Tools Collection](https://huggingface.co/spaces?sort=modified&search=smolagents+tool)
3. [CLI Documentation](https://huggingface.co/docs/smolagents/main/en/examples/cli)