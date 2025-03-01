import os
from typing import Optional, List, Dict, Any
from smolagents import (
    OpenAIServerModel, 
    CodeAgent, 
    Tool,
    tool,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    UserInputTool
)

# Initialize the model with Gemini 2.0 Flash
model = OpenAIServerModel(
    model_id="gemini-2.0-flash",
    api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.environ["GEMINI_API_KEY"]
)

@tool
def tool_search(query: str) -> str:
    """Search for a tool from HuggingFace Hub or available built-in tools.
    
    Args:
        query: Search query describing the tool functionality needed
    
    Returns:
        str: Description of available tools matching the query
    """
    try:
        from huggingface_hub import HfApi
        api = HfApi()
        
        # Search for tools in Hub spaces
        spaces = api.list_spaces(
            search=query,
            tags=["smolagents", "tool"],
            limit=5
        )
        
        results = ["Found tools:"]
        for space in spaces:
            results.append(f"- {space.id}: {space.cardData.get('description', 'No description')}")
        
        # Add info about built-in tools
        built_in = {
            "web_search": "DuckDuckGo web search",
            "visit_webpage": "Visit and read webpage content",
            "python_interpreter": "Execute Python code",
            "user_input": "Get input from user"
        }
        
        results.append("\nBuilt-in tools:")
        for name, desc in built_in.items():
            if query.lower() in name.lower() or query.lower() in desc.lower():
                results.append(f"- {name}: {desc}")
                
        return "\n".join(results)
    except Exception as e:
        return f"Error searching for tools: {str(e)}"

class ExtendableAgent:
    """An agent that can use Hub tools and built-in tools."""
    
    def __init__(self, model):
        # Start with basic tools
        self.tools = [
            DuckDuckGoSearchTool(),
            VisitWebpageTool(),
            tool_search,
            UserInputTool()
        ]
        
        self.agent = CodeAgent(
            tools=self.tools,
            model=model
        )
    
    def add_tool_from_hub(self, repo_id: str) -> bool:
        """Add a tool from HuggingFace Hub.
        
        Args:
            repo_id: Repository ID of the tool
            
        Returns:
            bool: True if tool was added successfully
        """
        try:
            new_tool = Tool.from_hub(repo_id)
            self.tools.append(new_tool)
            # Recreate agent with updated tools
            self.agent = CodeAgent(tools=self.tools, model=self.agent.model)
            return True
        except Exception as e:
            print(f"Failed to add tool {repo_id}: {str(e)}")
            return False
    
    def run(self, query: str) -> str:
        """Run a query with current tools."""
        return self.agent.run(query)

def main():
    # Create agent
    agent = ExtendableAgent(model)
    
    # Example: Search for and use tools
    query = """
    1. Search for tools related to "image processing"
    2. Tell me what tools you found
    3. Then search the web for "latest AI image processing techniques"
    4. Summarize the findings
    """
    
    result = agent.run(query)
    print("\nFinal Result:", result)

if __name__ == "__main__":
    main()