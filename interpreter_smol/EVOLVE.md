# 🧬 EVOLVE - The Self-Evolving Agent System

EVOLVE is a powerful AI system that can create, manage, and evolve specialized agents to help with any task. Think of it as a smart AI manager that can build and coordinate a team of AI specialists.

## 🚀 Quick Start

```bash
# Launch interactive mode
interpreter-evolve -i

# Or with custom settings
interpreter-evolve --model openai --workspace ./my_agents --verbose
```

## 🎯 Key Capabilities

### 1. 🤖 Agent Creation
```python
# Create a data analysis agent
interpreter-evolve "Create an agent that can:
1. Load and clean CSV files
2. Generate statistical summaries
3. Create visualizations
Name it 'data_wizard'"
```

### 2. 📊 Agent Management
```python
# List all agents
interpreter-evolve "List available agents"

# Use an agent
interpreter-evolve "Have data_wizard analyze sales_2024.csv"

# Delete an agent
interpreter-evolve "Delete the data_wizard agent"
```

### 3. 🔧 Tool Distribution
Agents can be equipped with various tools:
- 💻 Python code execution
- 🌐 Web search capabilities
- 📁 File operations
- 🖼️ Image processing
- 📊 Data analysis

### 4. 🧠 Smart Persistence
- Agents persist between sessions
- Workspace management
- State preservation
- Configuration memory

## 💡 Use Cases

### Data Analysis Agent
```bash
interpreter-evolve "Create a data analysis agent that can:
- Read CSV and Excel files
- Create summary statistics
- Generate plots
- Export reports"
```

### Web Research Agent
```bash
interpreter-evolve "Create a research agent that can:
- Search multiple sources
- Summarize findings
- Save citations
- Generate reports"
```

### System Monitor Agent
```bash
interpreter-evolve "Create a system monitor that:
- Tracks CPU and memory usage
- Alerts on high usage
- Logs performance metrics
- Generates reports"
```

## 🛠️ Technical Details

### Workspace Structure
```
agent_workspace/
├── agent_registry.json     # Agent metadata
├── data_wizard/           # Agent-specific directory
│   ├── data_wizard.py     # Agent implementation
│   └── config.yaml        # Agent configuration
└── research_agent/        # Another agent
    └── ...
```

### Agent Components
1. **Code**: Python implementation
2. **Configuration**: YAML settings
3. **Tools**: Assigned capabilities
4. **State**: Persistent memory

### Command Line Options
```bash
interpreter-evolve [options]
  -w, --workspace DIR    Set agent workspace
  -m, --model TYPE      Select AI model
  -v, --verbose        Enable detailed output
  -i, --interactive    Start interactive mode
```

## 🔐 Security & Permissions

The evolving agent system has full system access. Use responsibly:
- Only run in trusted environments
- Review agent code before deployment
- Monitor agent activities
- Use workspace isolation

## 🤝 Integration Examples

### With Python Scripts
```python
from interpreter_smol.agents import EvolvingAgentSystem

system = EvolvingAgentSystem(
    model_type="gemini",
    workspace_dir="./agents"
)

# Create an agent
system.run("""
Create an agent named 'file_manager' that can:
1. Organize files by type
2. Remove duplicates
3. Generate reports
""")

# Use the agent
system.run("file_manager, organize ./downloads")
```

### With Other Tools
```python
# Create an agent with specific tools
system.run("""
Create an agent with:
- Web search capability
- Python execution
- File operations
- Image processing
Name it 'media_assistant'
""")
```

## 📊 Best Practices

1. **Agent Design**
   - Clear, focused purpose
   - Appropriate tool selection
   - Error handling
   - Documentation

2. **Workspace Management**
   - Regular cleanup
   - Version control
   - Backup strategy

3. **Security**
   - Review agent code
   - Monitor activities
   - Restrict permissions

4. **Performance**
   - Task-appropriate tools
   - Resource monitoring
   - Code optimization

## 🔄 Evolution Process

1. **Creation**: Define agent purpose and capabilities
2. **Testing**: Verify functionality
3. **Deployment**: Add to workspace
4. **Monitoring**: Track performance
5. **Improvement**: Update based on feedback
6. **Collaboration**: Share with other agents

## 🎯 Tips & Tricks

1. **Agent Creation**
   - Be specific about capabilities
   - Include error handling
   - Add documentation

2. **Efficient Usage**
   - Use appropriate models
   - Leverage existing agents
   - Combine capabilities

3. **Troubleshooting**
   - Check logs
   - Review agent code
   - Test in isolation

## 🤝 Contributing

Want to help improve EVOLVE?
1. Fork the repository
2. Create your feature branch
3. Add your changes
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

Remember: EVOLVE is constantly learning and improving. The more you use it, the better it gets at creating and managing agents for your specific needs!