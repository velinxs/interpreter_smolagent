# EVOLVE - Self-Evolving AI Assistant

## What Is This?

EVOLVE is a smart AI assistant that can:
1. Talk to you like a normal AI chat
2. Run Python code to do things on your computer
3. Create specialized "mini-AIs" (agents) for specific tasks
4. Remember these agents and use them again later

Think of it like having one main AI assistant who can create and manage a team of specialized helpers.

## How to Start It

Just run this command:
```
python evolve.py
```

That's it! You'll get a chat prompt where you can start talking to the AI.

## Simple Things You Can Ask

### Run Code
```
Write a Python script that creates a file called "hello.txt" with the text "Hello World" in it.
```

### Search the Web
```
What were the top news stories yesterday?
```

### Create a Specialized Agent
```
Create an agent that can help me track my daily expenses.
```

### Use an Agent You Created Before
```
Use my expense tracker agent to add a $25 lunch expense for today.
```

## How It Works (Simple Version)

1. **Main AI**: This is your primary assistant that understands what you want
2. **Code Runner**: Lets the AI run Python code on your computer
3. **Agent Creator**: Lets the AI make specialized helpers
4. **Agent Storage**: Remembers all the helpers the AI has created

## Cool Features

- **Full System Access**: The AI can create files, run programs, etc.
- **Memory**: It remembers agents between sessions
- **Web Access**: It can search the web for information
- **Self-Improvement**: The more you use it, the better it gets at creating helpful agents

## Example Conversation

**You**: I need help managing my grocery shopping.

**EVOLVE**: I can help with that! Would you like me to create a specialized grocery assistant agent?

**You**: Yes, please.

**EVOLVE**: *Creates a grocery agent that can track shopping lists, suggest recipes, etc.*

**You**: Add milk, eggs, and bread to my shopping list.

**EVOLVE**: *Uses the grocery agent to update your shopping list*

## Important Notes

- The AI has access to your computer, so only use it in a trusted environment
- All agents are stored in the "agent_workspace" folder
- If something doesn't work, try asking the AI to fix it - that's what it's designed to do!

## Quick Commands

- Start interactive mode: `python evolve.py`
- Run a single command: `python evolve.py "your command here"`
- See all options: `python evolve.py --help`

That's it! Just start it up and talk to it like you would any AI assistant.