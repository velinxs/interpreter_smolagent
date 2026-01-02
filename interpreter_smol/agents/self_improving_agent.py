"""
Self-Improving Agent - Unlimited agent with dynamic tool creation

An enhanced agent that can:
- Create its own tools dynamically
- Introspect and understand its own codebase
- Deploy Claude Code agents for complex tasks
- Self-modify and improve
- Work autonomously with full system access
"""

from typing import List, Dict, Optional, Any, Type
from pathlib import Path
import json

from smolagents import CodeAgent, Tool
from smolagents.models import LiteLLMModel
from ..tools.dynamic_tool_factory import (
    ToolFactory,
    LLMToolGenerator,
    ToolSpec,
    create_tool_from_description
)
from ..tools.tool_registry import ToolRegistry, ToolMetadata
from ..tools.codebase_navigator import CodebaseNavigator
from ..tools.claude_agent_manager import ClaudeAgentManager


class SelfImprovingAgent:
    """
    A self-aware, self-improving agent with unlimited capabilities

    Features:
    - Dynamic tool creation from natural language
    - Codebase introspection and modification
    - Claude agent deployment for complex tasks
    - Persistent tool library
    - Full system access (unrestricted mode)
    """

    def __init__(
        self,
        model: str = "gemini",
        model_id: Optional[str] = None,
        initial_tools: Optional[List[str]] = None,
        allow_tool_creation: bool = True,
        allow_self_modification: bool = True,
        allow_claude_deployment: bool = True,
        project_root: Optional[Path] = None,
        workspace_dir: Optional[Path] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        verbose: bool = True
    ):
        """
        Initialize Self-Improving Agent

        Args:
            model: Model provider (gemini, openai, anthropic, etc.)
            model_id: Specific model ID
            initial_tools: Initial tools to load
            allow_tool_creation: Enable dynamic tool creation
            allow_self_modification: Enable codebase modification
            allow_claude_deployment: Enable Claude agent deployment
            project_root: Project root for codebase introspection
            workspace_dir: Workspace for agents and tools
            temperature: Model temperature
            max_tokens: Maximum tokens
            verbose: Print detailed information
        """
        self.verbose = verbose

        # Capabilities
        self.allow_tool_creation = allow_tool_creation
        self.allow_self_modification = allow_self_modification
        self.allow_claude_deployment = allow_claude_deployment

        # Initialize model
        self.model_name = model
        self.model = self._initialize_model(model, model_id, temperature, max_tokens)

        # Initialize tool system
        self.tool_factory = ToolFactory(strict_mode=False, verbose=verbose)
        self.tool_registry = ToolRegistry(
            storage_dir=workspace_dir / "tools" if workspace_dir else None,
            auto_save=True,
            verbose=verbose
        )

        # Initialize codebase navigator
        self.codebase_nav = CodebaseNavigator(
            project_root=project_root,
            verbose=verbose
        )

        # Initialize Claude agent manager
        self.claude_manager = ClaudeAgentManager(
            workspace_dir=workspace_dir / "claude_projects" if workspace_dir else None,
            verbose=verbose
        )

        # Load initial tools
        self._load_initial_tools(initial_tools or ["enhanced_python", "web_search"])

        # Create meta-tools (tools for creating tools, introspecting, etc.)
        self._create_meta_tools()

        # Initialize the underlying CodeAgent
        self.agent = self._create_agent()

        if self.verbose:
            print(f"[SelfImprovingAgent] Initialized with {len(self.get_available_tools())} tools")

    def _initialize_model(self, model: str, model_id: Optional[str], temperature: float, max_tokens: int):
        """Initialize the LLM model"""
        if model_id is None:
            # Default model IDs (updated for Gemini 3 - Dec 2025)
            model_ids = {
                "gemini": "gemini/gemini-3-flash-preview",  # Latest Gemini 3 Flash
                "gemini-flash": "gemini/gemini-3-flash-preview",  # Explicit Flash
                "gemini-pro": "gemini/gemini-3-pro-preview",  # Gemini 3 Pro for complex tasks
                "openai": "gpt-4",
                "anthropic": "claude-sonnet-4-5-20250929"
            }
            model_id = model_ids.get(model, "gemini/gemini-3-flash-preview")

        return LiteLLMModel(
            model_id=model_id,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def _load_initial_tools(self, tool_names: List[str]):
        """Load initial tools"""
        from ..tools.enhanced_python import EnhancedPythonInterpreter
        from smolagents.default_tools import TOOL_MAPPING

        # Tool mapping with enhanced Python
        available_tools = {
            "enhanced_python": EnhancedPythonInterpreter,
            **TOOL_MAPPING
        }

        for tool_name in tool_names:
            if tool_name in available_tools:
                tool_class = available_tools[tool_name]
                metadata = ToolMetadata(
                    name=tool_name,
                    description=getattr(tool_class, 'description', ''),
                    version="1.0.0",
                    author="system",
                    created_at="",
                    source="package"
                )
                self.tool_registry.register_tool(tool_class, metadata)

    def _create_meta_tools(self):
        """Create meta-tools for self-improvement"""

        # Tool creation tool
        if self.allow_tool_creation:
            self._register_tool_creation_tool()

        # Codebase introspection tools
        self._register_introspection_tools()

        # Claude deployment tool
        if self.allow_claude_deployment:
            self._register_claude_deployment_tool()

    def _register_tool_creation_tool(self):
        """Register tool for creating new tools"""

        class CreateToolTool(Tool):
            name = "create_tool"
            description = """Create a new tool dynamically from a description.

            Use this when you need a capability that doesn't exist in your current toolset.
            The tool will be created, tested, and added to your available tools automatically.

            Args:
                tool_description: Natural language description of what the tool should do
                tool_name: Optional name for the tool (will be auto-generated if not provided)

            Returns:
                Success message with tool name, or error message
            """
            inputs = {
                "tool_description": {
                    "type": "string",
                    "description": "What the tool should do"
                },
                "tool_name": {
                    "type": "string",
                    "description": "Optional tool name",
                    "nullable": True
                }
            }
            output_type = "string"

            def __init__(self, agent: 'SelfImprovingAgent'):
                super().__init__()
                self.agent = agent

            def forward(self, tool_description: str, tool_name: str = None) -> str:
                if not self.agent.allow_tool_creation:
                    return "Error: Tool creation is disabled"

                # Generate tool code
                generator = LLMToolGenerator(self.agent.model)
                code, error = generator.generate_tool(tool_description, tool_name)

                if error:
                    return f"Error generating tool: {error}"

                if tool_name is None:
                    tool_name = generator._generate_function_name(tool_description)

                # Create tool
                tool_class, error = self.agent.tool_factory.create_tool_from_code(
                    name=tool_name,
                    code=code,
                    description=tool_description
                )

                if error:
                    return f"Error creating tool: {error}"

                # Create spec for persistence
                spec = ToolSpec(
                    name=tool_name,
                    description=tool_description,
                    code=code,
                    inputs={},  # Could extract from code
                    output_type="string",
                    author="agent"
                )

                # Register tool
                metadata = ToolMetadata(
                    name=tool_name,
                    description=tool_description,
                    version="1.0.0",
                    author="agent",
                    created_at="",
                    source="runtime"
                )

                self.agent.tool_registry.register_tool(tool_class, metadata, spec)

                # Refresh agent tools
                self.agent._refresh_agent_tools()

                return f"Successfully created and registered tool '{tool_name}'. You can now use it in your workflow."

        # Instantiate with reference to this agent
        create_tool_instance = CreateToolTool(self)
        self.tool_registry.register_tool(
            CreateToolTool,
            ToolMetadata(
                name="create_tool",
                description="Create new tools dynamically",
                version="1.0.0",
                author="system",
                created_at="",
                source="meta"
            )
        )

    def _register_introspection_tools(self):
        """Register codebase introspection tools"""

        class ReadCodeTool(Tool):
            name = "read_code"
            description = "Read source code from the codebase"
            inputs = {
                "file_path": {"type": "string", "description": "Path to file"},
                "start_line": {"type": "integer", "description": "Optional start line", "nullable": True},
                "end_line": {"type": "integer", "description": "Optional end line", "nullable": True}
            }
            output_type = "string"

            def __init__(self, navigator: CodebaseNavigator):
                super().__init__()
                self.navigator = navigator

            def forward(self, file_path: str, start_line: int = None, end_line: int = None) -> str:
                content = self.navigator.read_file(file_path, start_line, end_line)
                return content if content else f"Error: Could not read {file_path}"

        class SearchCodeTool(Tool):
            name = "search_code"
            description = "Search for code patterns in the codebase"
            inputs = {
                "pattern": {"type": "string", "description": "Search pattern"},
                "file_pattern": {"type": "string", "description": "Optional file pattern like '*.py'", "nullable": True}
            }
            output_type = "string"

            def __init__(self, navigator: CodebaseNavigator):
                super().__init__()
                self.navigator = navigator

            def forward(self, pattern: str, file_pattern: str = None) -> str:
                matches = self.navigator.search_code(pattern, file_pattern)
                if not matches:
                    return f"No matches found for '{pattern}'"

                result = f"Found {len(matches)} matches:\n"
                for match in matches[:20]:  # Limit to 20 results
                    result += f"\n{match['file']}:{match['line']} {match['content']}"

                return result

        class GetProjectSummaryTool(Tool):
            name = "get_project_summary"
            description = "Get a summary of the project structure and statistics"
            inputs = {}
            output_type = "string"

            def __init__(self, navigator: CodebaseNavigator):
                super().__init__()
                self.navigator = navigator

            def forward(self) -> str:
                summary = self.navigator.get_project_summary()
                return json.dumps(summary, indent=2)

        # Register introspection tools
        for tool_class in [ReadCodeTool, SearchCodeTool, GetProjectSummaryTool]:
            instance = tool_class(self.codebase_nav)
            self.tool_registry.register_tool(
                tool_class,
                ToolMetadata(
                    name=tool_class.name,
                    description=tool_class.description,
                    version="1.0.0",
                    author="system",
                    created_at="",
                    source="meta"
                )
            )

    def _register_claude_deployment_tool(self):
        """Register tool for deploying Claude agents"""

        class DeployClaudeTool(Tool):
            name = "deploy_claude_agent"
            description = """Deploy a Claude Code agent in headless mode for complex autonomous tasks.

            Use this when you need Claude Opus's capabilities for:
            - Large-scale refactoring
            - Complex analysis requiring deep reasoning
            - Tasks that benefit from extended context
            - Parallel autonomous work

            The Claude agent will work with full permissions and autonomously complete the task.

            Args:
                task_description: Detailed description of what Claude should do
                model: Model to use (opus, sonnet, haiku) - default: opus
                wait_for_completion: Whether to wait for the agent to finish

            Returns:
                Task ID and status, or results if wait_for_completion=True
            """
            inputs = {
                "task_description": {
                    "type": "string",
                    "description": "Detailed task description for Claude"
                },
                "model": {
                    "type": "string",
                    "description": "Model to use: opus, sonnet, or haiku"
                },
                "wait_for_completion": {
                    "type": "boolean",
                    "description": "Whether to wait for completion"
                }
            }
            output_type = "string"

            def __init__(self, manager: ClaudeAgentManager):
                super().__init__()
                self.manager = manager

            def forward(
                self,
                task_description: str,
                model: str = "opus",
                wait_for_completion: bool = False
            ) -> str:
                task_id, error = self.manager.deploy_agent(
                    task_description=task_description,
                    model=model,
                    wait_for_completion=wait_for_completion
                )

                if error:
                    return f"Error deploying Claude agent: {error}"

                if wait_for_completion:
                    result = self.manager.get_task_result(task_id)
                    return f"Claude agent completed task {task_id}:\n\n{result}"
                else:
                    return f"Deployed Claude agent with task ID: {task_id}\nUse check_claude_agent('{task_id}') to check status."

        class CheckClaudeTool(Tool):
            name = "check_claude_agent"
            description = "Check the status of a deployed Claude agent"
            inputs = {
                "task_id": {"type": "string", "description": "Task ID from deployment"}
            }
            output_type = "string"

            def __init__(self, manager: ClaudeAgentManager):
                super().__init__()
                self.manager = manager

            def forward(self, task_id: str) -> str:
                status = self.manager.get_task_status(task_id)
                if not status:
                    return f"Error: Task {task_id} not found"

                result = f"Task {task_id} status: {status['status']}\n"
                result += f"Description: {status['description']}\n"

                if status['status'] == 'completed':
                    task_result = self.manager.get_task_result(task_id)
                    result += f"\nResult:\n{task_result}"
                elif 'recent_output' in status:
                    result += f"\nRecent output:\n" + "\n".join(status['recent_output'][-10:])

                return result

        # Register Claude tools
        for tool_class in [DeployClaudeTool, CheckClaudeTool]:
            instance = tool_class(self.claude_manager)
            self.tool_registry.register_tool(
                tool_class,
                ToolMetadata(
                    name=tool_class.name,
                    description=tool_class.description,
                    version="1.0.0",
                    author="system",
                    created_at="",
                    source="meta"
                )
            )

    def _create_agent(self) -> CodeAgent:
        """Create the underlying CodeAgent"""
        tools = [tool_class() for tool_class in self.tool_registry.get_all_tools().values()]

        # Load custom prompt
        prompt_path = Path(__file__).parent.parent / "prompts" / "self_aware_agent.yaml"
        additional_prompt = ""

        if prompt_path.exists():
            import yaml
            with open(prompt_path, 'r') as f:
                prompt_data = yaml.safe_load(f)
                additional_prompt = prompt_data.get('system_prompt', '')

        agent = CodeAgent(
            tools=tools,
            model=self.model,
            additional_authorized_imports=["os", "sys", "subprocess", "pathlib"],
            verbosity_level=2 if self.verbose else 1,
            max_steps=20  # Allow more steps for complex tasks
        )

        return agent

    def _refresh_agent_tools(self):
        """Refresh the agent's tool list"""
        new_tools = [tool_class() for tool_class in self.tool_registry.get_all_tools().values()]
        self.agent.tools = new_tools
        self.agent.toolbox = {tool.name: tool for tool in new_tools}

    def run(self, task: str) -> str:
        """
        Run a task

        Args:
            task: Task description

        Returns:
            Result
        """
        if self.verbose:
            print(f"\n[SelfImprovingAgent] Starting task: {task}\n")

        try:
            result = self.agent.run(task)
            return result
        except Exception as e:
            return f"Error executing task: {e}"

    def chat(self):
        """Start interactive chat mode"""
        print("=" * 60)
        print("Self-Improving Agent - Interactive Mode")
        print("=" * 60)
        print(f"\nCapabilities:")
        print(f"  - Dynamic tool creation: {self.allow_tool_creation}")
        print(f"  - Self-modification: {self.allow_self_modification}")
        print(f"  - Claude deployment: {self.allow_claude_deployment}")
        print(f"\nAvailable tools: {len(self.get_available_tools())}")
        print("\nType 'quit' to exit, 'help' for assistance\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break

                if user_input.lower() == 'help':
                    self._show_help()
                    continue

                if user_input.lower() == 'tools':
                    self._show_tools()
                    continue

                if not user_input:
                    continue

                result = self.run(user_input)
                print(f"\nAgent: {result}\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}\n")

    def _show_help(self):
        """Show help information"""
        print("\nHelp:")
        print("  - Ask me to do anything - I can create tools as needed")
        print("  - I can read and modify my own code")
        print("  - I can deploy Claude agents for complex tasks")
        print("  - Type 'tools' to see available tools")
        print("  - Type 'quit' to exit\n")

    def _show_tools(self):
        """Show available tools"""
        tools = self.tool_registry.list_tools()
        print(f"\nAvailable tools ({len(tools)}):")
        for tool_name in tools:
            info = self.tool_registry.get_tool_info(tool_name)
            if info:
                print(f"  - {tool_name}: {info['description'][:80]}")
        print()

    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return self.tool_registry.list_tools()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the agent"""
        return {
            "total_tools": len(self.get_available_tools()),
            "tool_registry_stats": self.tool_registry.get_stats(),
            "claude_agent_stats": self.claude_manager.get_stats(),
            "capabilities": {
                "tool_creation": self.allow_tool_creation,
                "self_modification": self.allow_self_modification,
                "claude_deployment": self.allow_claude_deployment
            }
        }
