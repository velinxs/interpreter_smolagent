"""
Example 1: Basic Self-Improving Agent

Demonstrates the basic capabilities of the self-improving agent:
- Running tasks
- Listing available tools
- Getting agent statistics
"""

from interpreter_smol.agents.self_improving_agent import SelfImprovingAgent

def main():
    print("=" * 60)
    print("Example 1: Basic Self-Improving Agent")
    print("=" * 60)

    # Initialize the agent
    print("\n1. Initializing agent...")
    agent = SelfImprovingAgent(
        model="gemini",
        verbose=True,
        allow_tool_creation=True,
        allow_claude_deployment=True
    )

    # Show initial tools
    print("\n2. Available tools:")
    for tool in agent.get_available_tools():
        print(f"   - {tool}")

    # Run a simple task
    print("\n3. Running a simple Python task...")
    result = agent.run("Calculate the first 10 Fibonacci numbers and display them")
    print(f"\nResult: {result}")

    # Show statistics
    print("\n4. Agent statistics:")
    stats = agent.get_stats()
    print(f"   Total tools: {stats['total_tools']}")
    print(f"   Tool creation enabled: {stats['capabilities']['tool_creation']}")
    print(f"   Claude deployment enabled: {stats['capabilities']['claude_deployment']}")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
