"""
Example 5: Complete Self-Improving Workflow

Demonstrates the full capabilities of the system in a realistic scenario:
- Dynamic tool creation
- Codebase introspection
- Tool persistence
- Complex multi-step tasks
"""

from interpreter_smol.agents.self_improving_agent import SelfImprovingAgent
from pathlib import Path


def main():
    print("=" * 70)
    print("Example 5: Complete Self-Improving Workflow")
    print("=" * 70)

    # Initialize agent
    print("\nInitializing self-improving agent...")
    agent = SelfImprovingAgent(
        model="gemini",
        verbose=True,
        allow_tool_creation=True,
        allow_self_modification=False,  # Be careful with this!
        allow_claude_deployment=True,
        project_root=Path.cwd()
    )

    print(f"\nStarting with {len(agent.get_available_tools())} tools")

    # Scenario: Data analysis workflow
    print("\n" + "=" * 70)
    print("SCENARIO: Build a data analysis workflow")
    print("=" * 70)

    workflow_task = """
    I'm going to work on a data analysis project. Here's what I need:

    1. First, introspect this codebase to understand the project structure
       Use get_project_summary to see what we're working with.

    2. Create a tool called 'generate_sample_data' that:
       - Generates sample CSV data with columns: name, age, city, salary
       - Creates 100 rows of realistic-looking data
       - Saves it to a file

    3. Create a tool called 'analyze_data_file' that:
       - Reads a CSV file
       - Calculates basic statistics (mean, median, std for numeric columns)
       - Counts unique values for text columns
       - Returns a formatted report

    4. Use both tools to:
       - Generate sample data
       - Analyze it
       - Show me the results

    Work through this step by step.
    """

    print("\nExecuting workflow...")
    result = agent.run(workflow_task)
    print(f"\n{result}")

    # Show what tools were created
    print("\n" + "=" * 70)
    print("Tools created during this session:")
    print("=" * 70)

    final_tools = agent.get_available_tools()
    print(f"\nTotal tools: {len(final_tools)}")

    # Show agent stats
    print("\n" + "=" * 70)
    print("Agent Statistics:")
    print("=" * 70)

    stats = agent.get_stats()
    print(f"\nTotal tools: {stats['total_tools']}")
    print(f"Tool registry: {stats['tool_registry_stats']}")

    print("\n" + "=" * 70)
    print("Workflow complete!")
    print("\nThe created tools are now saved and can be reused in future sessions.")
    print("Try running this again - the tools will already exist!")
    print("=" * 70)


def demonstrate_persistence():
    """Demonstrate that tools persist across sessions"""
    print("\n" + "=" * 70)
    print("BONUS: Demonstrating Tool Persistence")
    print("=" * 70)

    # Create a new agent instance (simulates new session)
    print("\nCreating a NEW agent instance (simulating new session)...")
    agent2 = SelfImprovingAgent(
        model="gemini",
        verbose=False
    )

    tools = agent2.get_available_tools()
    print(f"\nTools available in new session: {len(tools)}")
    print("\nTools from previous sessions were automatically loaded!")

    print("\nListing some tools:")
    for tool in list(tools)[:10]:
        info = agent2.tool_registry.get_tool_info(tool)
        if info:
            print(f"  • {tool}: {info['description'][:60]}")


if __name__ == "__main__":
    main()

    # Uncomment to see persistence demo
    # demonstrate_persistence()
