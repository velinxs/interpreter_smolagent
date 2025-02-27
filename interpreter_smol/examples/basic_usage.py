"""
examples/basic_usage.py - Examples of using interpreter-smol

This script shows various ways to use the interpreter-smol package,
from basic usage to more advanced configurations.
"""

import os
from interpreter_smol import Interpreter

def basic_example():
    """Basic usage with default settings (Gemini model)"""
    print("\n=== Basic Example (Gemini) ===")
    
    # Initialize the interpreter with default settings
    interpreter = Interpreter()
    
    # Run a simple prompt
    result = interpreter.run("Calculate the first 10 prime numbers and print them")
    
    print("\nResult:", result)


def custom_model_example():
    """Example using a different model provider"""
    print("\n=== Custom Model Example (OpenAI) ===")
    
    # Check if API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        print("Skipping OpenAI example - no API key found")
        print("Set the OPENAI_API_KEY environment variable to run this example")
        return
    
    # Initialize with OpenAI
    interpreter = Interpreter(
        model="openai",
        model_id="gpt-4o", 
        verbose=True
    )
    
    # Run a simple prompt
    interpreter.run("Write a function to check if a number is prime")


def custom_tools_example():
    """Example with specific tools enabled"""
    print("\n=== Custom Tools Example ===")
    
    # Initialize with specific tools
    interpreter = Interpreter(
        tools=["python_interpreter", "web_search"],
        imports=["numpy", "pandas", "matplotlib.pyplot"],
        verbose=True
    )
    
    # For demo purposes, we'll use a prompt that could use both tools
    interpreter.run("What is the current Bitcoin price? Create a simple bar chart showing the price compared to a $50,000 benchmark.")


def advanced_example():
    """More advanced usage with custom configuration"""
    print("\n=== Advanced Example ===")
    
    # More advanced configuration
    interpreter = Interpreter(
        model="gemini",  # Using Gemini
        model_id="gemini-2.0-flash",
        tools=["python_interpreter", "web_search", "visit_webpage"],
        imports=["numpy", "pandas", "matplotlib.pyplot", "seaborn", "sklearn"],
        temperature=0.3,  # Lower temperature for more deterministic results
        max_tokens=8000,
        verbose=True
    )
    
    # A more complex prompt
    prompt = """
    Find the current top cryptocurrency by market cap.
    Create a Python script that:
    1. Prints the name and current price
    2. Creates a simple visualization of its price compared to Bitcoin
    3. Analyzes the data and provides a brief summary
    """
    
    interpreter.run(prompt)


def interactive_mode_example():
    """Example showing how to use interactive mode"""
    print("\n=== Interactive Mode Example ===")
    print("Starting interactive session. Type 'exit' to end the session.")
    
    # Initialize the interpreter
    interpreter = Interpreter(verbose=True)
    
    # Start interactive session with an initial prompt
    interpreter.chat("Hello! I need help with some Python coding.")


if __name__ == "__main__":
    print("interpreter-smol Examples")
    print("------------------------")
    print("This script demonstrates different ways to use interpreter-smol.")
    
    # Run examples
    basic_example()
    
    # Uncomment these to run additional examples
    # custom_model_example()
    # custom_tools_example() 
    # advanced_example()
    # interactive_mode_example()  # This will start an interactive session
