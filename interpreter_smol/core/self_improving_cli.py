"""
CLI for the Self-Improving Agent

Entry point for running the unlimited self-improving agent
"""

import os
import sys
import argparse
from pathlib import Path

from ..agents.self_improving_agent import SelfImprovingAgent


def main():
    """Command line interface for self-improving agent"""
    parser = argparse.ArgumentParser(
        description="Self-Improving Agent: Unlimited AI with dynamic tool creation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  interpreter-unlimited

  # Run a specific task
  interpreter-unlimited "Create a tool for CSV analysis"

  # With specific model
  interpreter-unlimited --model openai "Analyze my codebase"

  # Enable Claude agent deployment
  interpreter-unlimited --claude "Deploy Claude to refactor this code"
"""
    )

    parser.add_argument(
        "task",
        nargs="?",
        help="Task to run (if not provided, starts interactive mode)"
    )

    parser.add_argument(
        "--model", "-m",
        default="gemini",
        choices=["gemini", "openai", "anthropic"],
        help="Model provider to use (default: gemini)"
    )

    parser.add_argument(
        "--model-id",
        default=None,
        help="Specific model ID (e.g., gpt-4, claude-opus-4-5-20251101)"
    )

    parser.add_argument(
        "--no-tool-creation",
        action="store_true",
        help="Disable dynamic tool creation"
    )

    parser.add_argument(
        "--no-self-mod",
        action="store_true",
        help="Disable self-modification capabilities"
    )

    parser.add_argument(
        "--no-claude",
        action="store_true",
        help="Disable Claude agent deployment"
    )

    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root for codebase introspection (default: current directory)"
    )

    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.home() / ".interpreter_smol",
        help="Workspace directory for tools and agents (default: ~/.interpreter_smol)"
    )

    parser.add_argument(
        "--temperature", "-t",
        type=float,
        default=0.7,
        help="Model temperature (default: 0.7)"
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=8192,
        help="Maximum tokens (default: 8192)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List all available tools and exit"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show agent statistics and exit"
    )

    args = parser.parse_args()

    # Print banner
    if not args.list_tools and not args.stats:
        print("=" * 60)
        print("Self-Improving Agent - Unlimited AI")
        print("=" * 60)
        print(f"Model: {args.model}")
        print(f"Tool creation: {not args.no_tool_creation}")
        print(f"Claude deployment: {not args.no_claude}")
        print("=" * 60)
        print()

    try:
        # Initialize agent
        agent = SelfImprovingAgent(
            model=args.model,
            model_id=args.model_id,
            allow_tool_creation=not args.no_tool_creation,
            allow_self_modification=not args.no_self_mod,
            allow_claude_deployment=not args.no_claude,
            project_root=args.project_root,
            workspace_dir=args.workspace,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            verbose=args.verbose
        )

        # Handle special commands
        if args.list_tools:
            tools = agent.get_available_tools()
            print(f"\nAvailable tools ({len(tools)}):")
            for tool in tools:
                info = agent.tool_registry.get_tool_info(tool)
                if info:
                    print(f"  • {tool}")
                    print(f"    {info['description'][:80]}")
            print()
            return

        if args.stats:
            stats = agent.get_stats()
            print("\nAgent Statistics:")
            print(f"  Total tools: {stats['total_tools']}")
            print(f"  Registry stats: {stats['tool_registry_stats']}")
            print(f"  Claude stats: {stats['claude_agent_stats']}")
            print(f"  Capabilities:")
            for cap, enabled in stats['capabilities'].items():
                print(f"    - {cap}: {enabled}")
            print()
            return

        # Run task or start interactive mode
        if args.task:
            result = agent.run(args.task)
            print(f"\nResult:\n{result}\n")
        else:
            agent.chat()

    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
