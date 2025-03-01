# SmoLAgents Tutorial with Gemini Integration

This tutorial provides a detailed guide on using SmoLAgents with Google's Gemini 2.0 Flash model through its OpenAI-compatible endpoint.

## Prerequisites

1. Python environment with venv
2. Google Gemini API key
3. SmoLAgents library installed

## Environment Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.\.venv\Scripts\activate  # On Windows
```

2. Install required packages:
```bash
pip install smolagents
```

3. Set up Gemini API key in your environment:
```bash
# Add to ~/.bashrc or equivalent
export GEMINI_API_KEY=your_api_key_here
```

## Integration with Gemini 2.0 Flash

Gemini can be integrated with SmoLAgents through its OpenAI-compatible endpoint. The endpoint URL is:
```
https://generativelanguage.googleapis.com/v1beta/openai/
```

## Working Example

Here's a complete working example that demonstrates:
- Setting up the Gemini model
- Creating custom tools
- Using built-in tools
- Running complex queries

```python
import os
from smolagents import OpenAIServerModel, CodeAgent, tool, DuckDuckGoSearchTool

# Initialize the model with Gemini 2.0 Flash
model = OpenAIServerModel(
    model_id="gemini-2.0-flash",  # Use Gemini 2.0 Flash model
    api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.environ["GEMINI_API_KEY"]
)

# Define a custom tool with proper docstring
@tool
def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression and return the result.
    
    Args:
        expression: The mathematical expression to evaluate as a string (e.g., '2 + 2')
    
    Returns:
        str: The result of the calculation or an error message
    """
    try:
        result = eval(expression, {"__builtins__": {}}, {"abs": abs, "round": round})
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"

# Create an agent with both custom and built-in tools
agent = CodeAgent(
    tools=[
        calculate,
        DuckDuckGoSearchTool()
    ],
    model=model
)

# Test the agent with a complex task
result = agent.run("""
1. Search for the current population of Tokyo
2. Calculate what would be 0.1% of that population
Please provide both the search results and the calculation.
""")

print("Agent response:", result)
```

## Important Notes

1. **Tool Documentation**: Every custom tool must have:
   - Type hints for arguments and return value
   - Docstring with Args and Returns sections
   - Clear description of functionality

2. **Model Configuration**:
   - Use `OpenAIServerModel` for Gemini integration
   - Specify the correct endpoint URL
   - Ensure API key is available in environment

3. **Agent Types**:
   - `CodeAgent` is recommended over `ToolCallingAgent`
   - CodeAgent writes actions as Python code
   - More efficient with 30% fewer steps

4. **Error Handling**:
   - Always validate API key presence
   - Handle tool exceptions gracefully
   - Check tool return values

## Example Output

The example above produces output showing:
- Step-by-step execution
- Tool usage (web search and calculation)
- Token counts for each step
- Final formatted response

## Common Issues

1. **API Key Issues**:
   ```python
   # Check if API key is set
   if "GEMINI_API_KEY" not in os.environ:
       raise ValueError("GEMINI_API_KEY not found in environment")
   ```

2. **Tool Documentation Errors**:
   - Missing parameter descriptions will raise DocstringParsingException
   - Always include complete docstrings

3. **Model Response Format**:
   - The model may need multiple attempts to format final_answer correctly
   - This is normal and handled automatically

## Best Practices

1. **Tool Design**:
   - Keep tools simple and focused
   - Use clear, descriptive names
   - Include comprehensive documentation

2. **Security**:
   - Sanitize tool inputs
   - Limit tool capabilities appropriately
   - Use environment variables for sensitive data

3. **Performance**:
   - Monitor token usage
   - Use appropriate model parameters
   - Cache results when possible

## Resources

- [SmoLAgents Documentation](https://huggingface.co/docs/smolagents/index)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [OpenAI Compatibility Guide](https://ai.google.dev/docs/openai_compatibility)