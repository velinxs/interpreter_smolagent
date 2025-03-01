# Example of using SmoLAgents with Gemini 2.0 Flash
import os
from smolagents import OpenAIServerModel, CodeAgent, tool, DuckDuckGoSearchTool

# Validate environment
if "GEMINI_API_KEY" not in os.environ:
    raise ValueError("GEMINI_API_KEY not found in environment")

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
        # Use a restricted set of builtins for safety
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
test_query = """
1. Search for the current population of Tokyo
2. Calculate what would be 0.1% of that population
Please provide both the search results and the calculation.
"""

print("Executing query:", test_query)
result = agent.run(test_query)
print("\nAgent response:", result)