# Simple AI Agents

A collection of minimal AI agents built with different frameworks. Each one fits in a single file, has a couple of tools, and runs with an interactive chat loop.

The goal is simple — learn how agents work by building them from scratch, one framework at a time.

## Agents

### `gemini/` — Google Gemini

Uses Gemini 2.5 Flash with manual tool calling (no auto-execution). The agent can look up your IP, find your location, and check the weather.

**Tools:** `get_ip_address`, `get_location`, `get_weather`

```bash
cd gemini
cp .env.example .env          # add your GOOGLE_API_KEY
uv sync                       # or pip install google-genai httpx python-dotenv
python agent.py
```

### `langchain/` — LangChain + Ollama

Uses LangChain with Ollama for a fully local, zero-cost setup. Runs llama3.2 (3B) on your machine — no API keys needed.

**Tools:** `get_current_time`, `calculate`, `get_ip_address`

```bash
cd langchain

# one-time setup
brew install ollama
ollama serve                  # keep running in background
ollama pull llama3.2          # ~2GB download

python -m venv venv && source venv/bin/activate
pip install langchain langchain-ollama langgraph
python agent.py
```

### `strands/` — coming soon

## How It Works

All agents follow the same pattern:

```
You ask a question
  → Agent thinks about it
    → Picks a tool (or not)
      → Runs the tool
        → Thinks again (loops if needed)
          → Gives you an answer
```

This is the ReAct (Reason + Act) pattern. The LLM decides what to do, does it, observes the result, and repeats until it has an answer.

## License

MIT
