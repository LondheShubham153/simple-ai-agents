"""Simple AI Agent using LangChain + Ollama (free, local LLM)."""

import urllib.request
from datetime import datetime

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_ollama import ChatOllama


# --- Tools ---


@tool
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def calculate(expression: str) -> str:
    """Evaluate a simple math expression. Example: '42 * 17 + 3'"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"


@tool
def get_ip_address() -> str:
    """Get the user's public IP address."""
    try:
        ip = urllib.request.urlopen("https://api.ipify.org").read().decode()
        return ip
    except Exception as e:
        return f"Error: {e}"


# --- Agent ---

llm = ChatOllama(model="llama3.2")
tools = [get_current_time, calculate, get_ip_address]
agent = create_agent(llm, tools)


# --- Interactive Loop ---

def main():
    print("AI Agent ready! (type 'quit' to exit)")
    print("Tools available: get_current_time, calculate, get_ip_address\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        response = agent.invoke({"messages": [("user", user_input)]})
        # The last message in the response is the agent's final answer
        print(f"Agent: {response['messages'][-1].content}\n")


if __name__ == "__main__":
    main()
