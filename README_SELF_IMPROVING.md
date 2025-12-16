# Self-Improving Agent - Open Interpreter Experience with SmolaGents

An **unlimited AI agent** that can create its own tools, understand its own codebase, and deploy Claude Code agents for autonomous work.

## 🚀 Key Features

### 1. **Dynamic Tool Creation (MCP-Equivalent)**
Create tools on-the-fly from natural language descriptions:
```python
agent.run("Create a tool to analyze CSV files for data quality issues, then use it on data.csv")
```

The agent will:
- Generate Python code for the tool
- Test and validate it
- Register it in the tool registry
- Use it immediately
- Persist it for future sessions

### 2. **Codebase Self-Awareness**
The agent can introspect and understand its own code:
```python
agent.run("Show me how you implement tool creation internally")
```

Capabilities:
- Read its own source files
- Search for patterns across the codebase
- Understand dependencies and structure
- Explain its own implementation
- Modify itself (with caution)

### 3. **Claude Agent Deployment**
Deploy Claude Code agents in headless mode for complex autonomous tasks:
```python
agent.run("Deploy a Claude Opus agent to refactor all error handling in this codebase")
```

Features:
- Full permissions (file, bash, web access)
- Autonomous operation
- Multiple concurrent agents
- Progress monitoring
- Result retrieval

### 4. **Unlimited Access**
- Unrestricted Python execution
- Full filesystem access
- System command execution
- Network access
- Self-modification capabilities

## 📦 Installation

```bash
# Install the package
pip install -e .

# Set up API keys
export GEMINI_API_KEY="your-key-here"  # or OPENAI_API_KEY, ANTHROPIC_API_KEY
```

## 🎯 Quick Start

### Basic Usage

```python
from interpreter_smol.agents.self_improving_agent import SelfImprovingAgent

# Initialize
agent = SelfImprovingAgent(
    model="gemini",
    verbose=True,
    allow_tool_creation=True,
    allow_claude_deployment=True
)

# Run tasks
result = agent.run("Calculate prime numbers up to 100")
print(result)

# Interactive mode
agent.chat()
```

### Create Tools Dynamically

```python
# The agent creates tools as needed
agent.run("""
I need to fetch stock prices from Yahoo Finance.
Create a tool for this, then get the current price of AAPL.
""")

# Tool is now available for future use
agent.run("Get the price of GOOGL using the stock price tool")
```

### Introspect Codebase

```python
# Agent understands itself
agent.run("""
1. Show me the project structure
2. Find where ToolFactory is implemented
3. Explain how tool creation works
""")
```

### Deploy Claude Agents

```python
# For complex tasks requiring deep reasoning
agent.run("""
Deploy a Claude Opus agent in headless mode to:
1. Analyze the entire codebase for security vulnerabilities
2. Suggest fixes for each issue
3. Implement the top 5 critical fixes
4. Run tests to verify

Grant full permissions and let it work autonomously.
""")

# Check status later
agent.run("Check the status of the Claude agent")
```

## 🏗️ Architecture

### Core Components

1. **ToolFactory** (`tools/dynamic_tool_factory.py`)
   - Creates tools from code or natural language
   - Validates and tests tools
   - Manages tool specifications

2. **ToolRegistry** (`tools/tool_registry.py`)
   - Central tool management
   - Persistent storage
   - Tool discovery and versioning

3. **CodebaseNavigator** (`tools/codebase_navigator.py`)
   - File system introspection
   - Code search and analysis
   - Project structure understanding

4. **ClaudeAgentManager** (`tools/claude_agent_manager.py`)
   - Deploy Claude Code agents
   - Headless mode management
   - Task monitoring and results

5. **SelfImprovingAgent** (`agents/self_improving_agent.py`)
   - Main agent orchestration
   - Tool creation workflow
   - Autonomous operation

### Tool Storage

Tools are stored in `~/.interpreter_smol/tools/`:
```
~/.interpreter_smol/
├── tools/
│   ├── registry.json           # Tool metadata
│   ├── my_tool.py              # Tool code
│   └── my_tool.json            # Tool spec
└── claude_projects/            # Claude agent workspaces
    └── task_xxx/
        ├── TASK.md
        └── workspace/
```

## 📚 Examples

Run the provided examples:

```bash
# Basic usage
python examples/01_basic_self_improving_agent.py

# Dynamic tool creation
python examples/02_dynamic_tool_creation.py

# Codebase introspection
python examples/03_codebase_introspection.py

# Claude agent deployment
python examples/04_claude_agent_deployment.py
```

## 🔧 Configuration

### Agent Configuration

```python
agent = SelfImprovingAgent(
    model="gemini",                      # or "openai", "anthropic"
    model_id="gemini/gemini-2.0-flash-exp",  # specific model ID
    allow_tool_creation=True,            # Enable dynamic tools
    allow_self_modification=True,        # Enable code modification
    allow_claude_deployment=True,        # Enable Claude agents
    project_root=Path.cwd(),             # Project root for introspection
    workspace_dir=Path("~/.interpreter_smol"),  # Storage directory
    temperature=0.7,
    max_tokens=8192,
    verbose=True
)
```

### Claude Agent Configuration

Claude agents require Claude Code CLI to be installed and configured:

```bash
# Install Claude Code (if not already installed)
# Follow: https://github.com/anthropics/claude-code

# Claude agents will use:
# - Model: opus-4.5 (or sonnet, haiku)
# - Mode: headless with auto-approve
# - Permissions: full (file, bash, web, etc.)
```

## 🎨 Use Cases

### 1. Data Analysis Pipeline
```python
agent.run("""
1. Create a tool to load and validate CSV data
2. Create a tool to detect outliers
3. Create a tool to generate visualizations
4. Use all three tools to analyze sales_data.csv
5. Save a report with findings
""")
```

### 2. Code Refactoring
```python
agent.run("""
Deploy a Claude Opus agent to:
1. Find all functions longer than 50 lines
2. Refactor them into smaller, focused functions
3. Ensure all tests still pass
4. Commit the changes
""")
```

### 3. API Integration
```python
agent.run("""
Create tools to interact with the GitHub API:
1. Tool to list repositories
2. Tool to create issues
3. Tool to fetch pull requests

Then use them to analyze my top 5 repos.
""")
```

### 4. Self-Improvement
```python
agent.run("""
Analyze your own ToolFactory implementation.
Identify potential improvements.
Create a detailed plan for optimization.
""")
```

## 🔒 Security Considerations

### Unrestricted Mode (Default)
- Full system access
- Unrestricted Python execution
- Shell command execution
- File system modifications
- **Use with caution in production**

### Safety Features
- Tool validation before execution
- Syntax checking
- Optional approval workflows
- Audit logging
- Rollback capabilities

### Best Practices
1. Review generated tools before using in production
2. Use sandboxing for untrusted code
3. Monitor Claude agent activities
4. Keep backups before self-modifications
5. Use version control for all changes

## 🤝 Comparison with MCP

| Feature | MCP (Claude) | This System (SmolaGents) |
|---------|-------------|--------------------------|
| Tool Format | JSON schemas + external servers | Python code |
| Tool Creation | Manual development | Dynamic LLM generation |
| Runtime | Requires server process | Native Python |
| Persistence | Server-based | File-based |
| Language | Any (via IPC) | Python |
| Self-aware | No | Yes |
| Agent Deployment | N/A | Claude Code integration |

## 🚀 Advanced Features

### Custom Tool Templates

```python
from interpreter_smol.tools.dynamic_tool_factory import ToolSpec

spec = ToolSpec(
    name="my_tool",
    description="Does something useful",
    code="""
def my_tool(input: str) -> str:
    '''Tool that does something'''
    # Implementation
    return result
    """,
    inputs={"input": {"type": "string", "description": "Input data"}},
    output_type="string"
)

agent.tool_factory.create_tool_from_spec(spec)
```

### Tool Versioning

Tools are automatically versioned. Access previous versions:

```python
# Registry maintains version history
agent.tool_registry.get_tool_version("my_tool", "1.0.0")
```

### Multi-Agent Orchestration

```python
# Deploy multiple Claude agents in parallel
agent.run("""
Deploy 3 Claude agents to work in parallel:
1. Agent 1: Performance optimization
2. Agent 2: Security audit
3. Agent 3: Documentation generation

Monitor all and aggregate results.
""")
```

## 📖 API Reference

### SelfImprovingAgent

```python
class SelfImprovingAgent:
    def __init__(self, model, allow_tool_creation=True, ...)
    def run(self, task: str) -> str
    def chat(self)
    def get_available_tools(self) -> List[str]
    def get_stats(self) -> Dict[str, Any]
```

### ToolFactory

```python
class ToolFactory:
    def create_tool_from_code(self, name, code, description) -> Tuple[Type, Optional[str]]
    def create_tool_from_spec(self, spec: ToolSpec) -> Tuple[Type, Optional[str]]
```

### ToolRegistry

```python
class ToolRegistry:
    def register_tool(self, tool_class, metadata, spec)
    def get_tool(self, tool_name) -> Optional[Type]
    def list_tools(self, source=None, tags=None) -> List[str]
    def search_tools(self, query) -> List[str]
```

### ClaudeAgentManager

```python
class ClaudeAgentManager:
    def deploy_agent(self, task_description, model="opus", wait_for_completion=False)
    def get_task_status(self, task_id) -> Optional[Dict]
    def wait_for_agent(self, task_id, timeout=None) -> bool
    def get_task_result(self, task_id) -> Optional[str]
```

## 🐛 Troubleshooting

### Tool Creation Fails
- Check model API keys are set
- Verify internet connection
- Try with simpler tool descriptions
- Check logs for specific errors

### Claude Agent Not Starting
- Ensure Claude Code CLI is installed
- Verify `claude` command is in PATH
- Check Claude API key is configured
- Review task description for clarity

### Tools Not Persisting
- Check write permissions for `~/.interpreter_smol/`
- Verify `auto_save=True` in ToolRegistry
- Check disk space

## 🤔 FAQ

**Q: How is this different from Open Interpreter?**
A: We use smolagents (Python-based tools) instead of functions, support dynamic tool creation, have codebase self-awareness, and can deploy Claude agents for complex tasks.

**Q: Can tools persist across sessions?**
A: Yes! Tools are saved to `~/.interpreter_smol/tools/` and automatically loaded on startup.

**Q: Is it safe to allow self-modification?**
A: Use with caution. Enable only in trusted environments. Always use version control.

**Q: What models are supported?**
A: Gemini (default), OpenAI (GPT-4), Anthropic (Claude), and HuggingFace models via LiteLLM.

**Q: Can I use this in production?**
A: Yes, but review generated tools and consider sandboxing. Start with restricted permissions.

## 📝 License

Same as the base project.

## 🙏 Acknowledgments

- Built on [SmolaGents](https://github.com/huggingface/smolagents)
- Inspired by [Open Interpreter](https://github.com/KillianLucas/open-interpreter)
- Claude Code integration for autonomous agents
- MCP (Model Context Protocol) concepts

## 🔗 Links

- [Architecture Documentation](ARCHITECTURE.md)
- [Examples Directory](examples/)
- [SmolaGents Docs](https://github.com/huggingface/smolagents)
- [Claude Code](https://github.com/anthropics/claude-code)

---

**Ready to build an unlimited AI agent? Start with the examples and let your agent improve itself!** 🚀
