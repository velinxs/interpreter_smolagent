"""
Example 2: Dynamic Tool Creation

Demonstrates how the agent can create its own tools on-the-fly
"""

from interpreter_smol.agents.self_improving_agent import SelfImprovingAgent

def main():
    print("=" * 60)
    print("Example 2: Dynamic Tool Creation")
    print("=" * 60)

    # Initialize agent
    agent = SelfImprovingAgent(
        model="gemini",
        verbose=True
    )

    print(f"\nInitial tool count: {len(agent.get_available_tools())}")

    # Ask agent to create a tool and use it
    print("\n" + "=" * 60)
    print("Task: Create a tool for analyzing log files")
    print("=" * 60)

    task = """
    I need to analyze log files for errors and warnings.

    First, create a tool called 'analyze_logs' that:
    1. Reads a log file
    2. Counts errors (lines containing 'ERROR')
    3. Counts warnings (lines containing 'WARNING')
    4. Returns a summary

    Then, create a sample log file and test the tool on it.
    """

    result = agent.run(task)
    print(f"\nResult:\n{result}")

    # Check if tool was added
    print(f"\nFinal tool count: {len(agent.get_available_tools())}")
    print("\nAll available tools:")
    for tool in agent.get_available_tools():
        print(f"   - {tool}")

    print("\n" + "=" * 60)
    print("Tool persists across sessions - try running this again!")
    print("=" * 60)

if __name__ == "__main__":
    main()
