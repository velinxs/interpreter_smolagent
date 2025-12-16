"""
Example 4: Claude Agent Deployment

Demonstrates how to deploy Claude Code agents in headless mode
for complex autonomous tasks
"""

from interpreter_smol.agents.self_improving_agent import SelfImprovingAgent
import time

def main():
    print("=" * 60)
    print("Example 4: Claude Agent Deployment")
    print("=" * 60)

    # Initialize agent
    agent = SelfImprovingAgent(
        model="gemini",
        verbose=True,
        allow_claude_deployment=True
    )

    # Example 1: Deploy Claude for a complex task
    print("\n" + "=" * 60)
    print("Deploying Claude Opus for code analysis")
    print("=" * 60)

    task = """
    Deploy a Claude Opus agent in headless mode to:

    1. Analyze all Python files in the 'interpreter_smol/tools' directory
    2. Create a comprehensive documentation file explaining:
       - What each tool does
       - How they work together
       - Usage examples for each
    3. Save the documentation as 'TOOLS_GUIDE.md'

    Deploy the agent but don't wait for completion - return the task ID.
    """

    print("\nDeploying Claude agent...")
    result = agent.run(task)
    print(f"\nDeployment result:\n{result}")

    # Example 2: Check agent status
    print("\n" + "=" * 60)
    print("Checking Claude agent status")
    print("=" * 60)

    # Note: In a real scenario, you would extract the task_id from the result
    # For this example, we'll show how to check status

    check_task = """
    Check the status of all deployed Claude agents using the Claude manager.
    Show me what tasks are running or completed.
    """

    print("\nChecking status...")
    result = agent.run(check_task)
    print(f"\nStatus:\n{result}")

    # Example 3: Deploy multiple Claude agents in parallel
    print("\n" + "=" * 60)
    print("Deploying multiple Claude agents")
    print("=" * 60)

    parallel_task = """
    For demonstration purposes, show how you would deploy 3 Claude agents
    in parallel to work on different tasks:

    1. Agent 1: Analyze code quality
    2. Agent 2: Generate test cases
    3. Agent 3: Create documentation

    Explain the process (don't actually deploy if Claude Code CLI isn't set up).
    """

    result = agent.run(parallel_task)
    print(f"\nParallel deployment strategy:\n{result}")

    print("\n" + "=" * 60)
    print("Claude agents work autonomously with full permissions!")
    print("=" * 60)

if __name__ == "__main__":
    main()
