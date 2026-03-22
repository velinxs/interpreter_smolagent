# Gemini 3 Model Guide (December 2025)

## 🆕 Latest Models

### Gemini 3 Flash (Recommended) ⚡
- **Model ID**: `gemini/gemini-3-flash-preview`
- **Released**: December 17, 2025
- **Pricing**:
  - Input: **$0.50 per 1M tokens**
  - Output: **$3 per 1M tokens**
- **Context**: 1M input tokens, 64k output tokens
- **Knowledge Cutoff**: January 2025
- **Best For**:
  - 95% of tasks
  - Most cost-effective for production
  - Fastest frontier model
  - Dynamic tool creation
  - Code execution
  - General automation

### Gemini 3 Pro 🧠
- **Model ID**: `gemini/gemini-3-pro-preview`
- **Pricing** (≤200k tokens):
  - Input: **$2 per 1M tokens**
  - Output: **$12 per 1M tokens**
- **Pricing** (>200k tokens):
  - Input: **$4 per 1M tokens**
  - Output: **$18 per 1M tokens**
- **Context**: 1M input tokens, 64k output tokens
- **Best For**:
  - Complex reasoning tasks
  - Advanced agentic workflows
  - Deep code analysis
  - Adaptive thinking scenarios

## 💡 Usage Examples

### Default (Gemini 3 Flash)
```python
from interpreter_smol.agents.self_improving_agent import SelfImprovingAgent

# Automatically uses Gemini 3 Flash
agent = SelfImprovingAgent()
```

### Explicit Gemini 3 Flash
```python
agent = SelfImprovingAgent(
    model="gemini",  # or "gemini-flash"
    model_id="gemini/gemini-3-flash-preview"
)
```

### Gemini 3 Pro (for complex tasks)
```python
agent = SelfImprovingAgent(
    model="gemini-pro",
    # or explicitly:
    # model_id="gemini/gemini-3-pro-preview"
)
```

### CLI Usage
```bash
# Default (Gemini 3 Flash)
interpreter-unlimited

# Explicit Gemini 3 Flash
interpreter-unlimited --model gemini

# Gemini 3 Pro
interpreter-unlimited --model gemini-pro

# Custom model ID
interpreter-unlimited --model gemini --model-id "gemini/gemini-3-flash-preview"
```

## 📊 Cost Estimates

### Typical Tasks with Gemini 3 Flash

| Task | Est. Tokens | Est. Cost |
|------|------------|-----------|
| Create a simple tool | ~5k input, 2k output | $0.01 |
| Analyze CSV file | ~10k input, 5k output | $0.02 |
| Introspect codebase | ~20k input, 10k output | $0.04 |
| Build complex pipeline | ~50k input, 20k output | $0.09 |
| Full project analysis | ~200k input, 50k output | $0.25 |

### Monthly Usage Example

If you run **1000 tasks per month** with average 10k input / 5k output tokens each:
- Input: 10M tokens × $0.50 = **$5**
- Output: 5M tokens × $3 = **$15**
- **Total: ~$20/month**

Compare to Claude Opus:
- Same usage would cost **~$450/month** 😱

## 🎯 Recommendations

### For Most Users
✅ **Use Gemini 3 Flash** (default)
- Excellent performance
- Very affordable
- 1M context window
- Perfect for tool creation and automation

### When to Use Gemini 3 Pro
🧠 Use when you need:
- Extended reasoning chains
- Complex architectural decisions
- Deep code analysis across massive codebases
- Tasks requiring >200k context regularly

### When to Deploy Claude Opus
💎 Reserve for:
- Mission-critical refactoring
- Security audits requiring highest accuracy
- Projects where cost < accuracy
- Tasks benefiting from Claude's specific strengths

## 🔧 Configuration

### Environment Setup
```bash
# Required
export GEMINI_API_KEY="your-api-key-here"

# Optional (only if using Claude deployment)
export ANTHROPIC_API_KEY="your-claude-key"
```

### Python Config
```python
agent = SelfImprovingAgent(
    model="gemini",                     # Uses Gemini 3 Flash
    allow_tool_creation=True,           # ✅
    allow_claude_deployment=False,      # ❌ Disable for cost savings
    temperature=0.7,                    # Balanced creativity
    max_tokens=8192,                    # Sufficient for most tasks
    verbose=True
)
```

## 🚀 Performance Notes

### Gemini 3 Flash Benchmarks
- **GPQA Diamond**: 90.4% (vs 86.5% for Gemini 2.5 Pro)
- **SWE-bench Verified**: 78% (outperforms Gemini 3 Pro!)
- **Humanity's Last Exam**: 33.7%
- **Speed**: 3x faster than Gemini 2.5 Pro
- **Cost**: ~83% cheaper than Gemini 2.5 Pro

### Context Caching
Both Gemini 3 models support context caching:
- **90% cost reduction** on repeated token use
- Automatically enabled
- Great for iterative tasks

### Batch API
Available for 50% cost savings:
- Use for asynchronous tasks
- Higher rate limits
- Perfect for bulk operations

## 📚 References

- [Gemini 3 Flash Announcement](https://blog.google/products/gemini/gemini-3-flash/)
- [Gemini 3 Developer Guide](https://ai.google.dev/gemini-api/docs/gemini-3)
- [Pricing Documentation](https://ai.google.dev/gemini-api/docs/pricing)
- [Model Comparison](https://deepmind.google/models/gemini/)

---

**Last Updated**: December 21, 2025
**Current Default**: Gemini 3 Flash Preview
