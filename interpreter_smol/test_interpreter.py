"""
Test script for the Interpreter class with a mock model.
"""

import os
import sys
from typing import List, Dict, Any, Optional

# Mock the necessary components
class MockModel:
    def __init__(self, *args, **kwargs):
        pass
    
    def generate(self, *args, **kwargs):
        return "This is a mock response from the model."

class MockCodeAgent:
    def __init__(self, tools=None, model=None, additional_authorized_imports=None, verbosity_level=1):
        self.tools = tools or []
        self.model = model
        self.verbosity_level = verbosity_level
    
    def run(self, prompt, reset=True):
        print(f"Mock agent running prompt: {prompt}")
        return "Mock agent response"

# Import the Interpreter class
from cli import Interpreter

# Override the _initialize_model and _initialize_agent methods
class TestInterpreter(Interpreter):
    def _initialize_model(self):
        return MockModel()
    
    def _initialize_agent(self, tool_names, imports):
        return MockCodeAgent(verbosity_level=2 if self.verbose else 1)

def main():
    # Create an instance of the TestInterpreter
    interpreter = TestInterpreter(verbose=True)
    
    # Test running a prompt
    print("\nTesting run method...")
    result = interpreter.run("Test prompt")
    print(f"Result: {result}")
    
    # Test chat method with a single input
    print("\nTesting chat method with a single input...")
    try:
        # Simulate user input
        import builtins
        original_input = builtins.input
        builtins.input = lambda _: "exit"
        
        interpreter.chat("Initial prompt")
        
        # Restore original input function
        builtins.input = original_input
        print("Chat test completed successfully!")
    except Exception as e:
        print(f"Error in chat test: {e}")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main()