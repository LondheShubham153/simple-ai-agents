"""Simple Strands AI agent with tool calling.

Run:  python agent.py
Needs: AWS credentials configured (via env vars, ~/.aws/credentials, or SSO)
"""

from strands import Agent
from strands.models import BedrockModel

from tools import get_ip_address, get_location, get_weather

SYSTEM_PROMPT = (
    "You are a helpful agent that can use tools to answer questions. "
    "If no tools are needed, respond in haikus."
)
MODEL = "us.anthropic.claude-sonnet-4-20250514-v1:0"


def main():
    model = BedrockModel(model_id=MODEL, temperature=0.7)
    agent = Agent(
        model=model,
        tools=[get_ip_address, get_location, get_weather],
        system_prompt=SYSTEM_PROMPT,
        callback_handler=None,
    )

    print("Chat with the AI agent (type 'quit' to exit)\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            break

        result = agent(user_input)
        print(f"\nAgent: {result.message['content'][0]['text']}\n")


if __name__ == "__main__":
    main()
