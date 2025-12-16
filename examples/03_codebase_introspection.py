"""
Example 3: Codebase Introspection

Demonstrates how the agent can introspect and understand its own codebase
"""

from interpreter_smol.agents.self_improving_agent import SelfImprovingAgent

def main():
    print("=" * 60)
    print("Example 3: Codebase Introspection")
    print("=" * 60)

    # Initialize agent
    agent = SelfImprovingAgent(
        model="gemini",
        verbose=True
    )

    # Task 1: Understand project structure
    print("\n" + "=" * 60)
    print("Task 1: Get project summary")
    print("=" * 60)

    result = agent.run("""
    Use get_project_summary to show me an overview of this project's structure.
    """)
    print(f"\nResult:\n{result}")

    # Task 2: Find specific functionality
    print("\n" + "=" * 60)
    print("Task 2: Find tool creation code")
    print("=" * 60)

    result = agent.run("""
    Search the codebase for 'ToolFactory' and show me where it's defined.
    Then read the relevant file to explain how tool creation works.
    """)
    print(f"\nResult:\n{result}")

    # Task 3: Self-reflection
    print("\n" + "=" * 60)
    print("Task 3: Explain your own capabilities")
    print("=" * 60)

    result = agent.run("""
    Read your own SelfImprovingAgent class definition and explain:
    1. What capabilities you have
    2. How you create tools
    3. How you introspect code

    Be concise but specific.
    """)
    print(f"\nResult:\n{result}")

    print("\n" + "=" * 60)
    print("The agent understands its own implementation!")
    print("=" * 60)

if __name__ == "__main__":
    main()
