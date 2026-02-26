"""Simple Gemini AI agent with tool calling.

Run:  python agent.py
Needs: GOOGLE_API_KEY in .env (copy .env.example)
"""

import asyncio
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import execute_tool, get_tools

SYSTEM_INSTRUCTION = (
    "You are a helpful agent that can use tools to answer questions. "
    "If no tools are needed, respond in haikus."
)
MODEL = "gemini-2.5-flash"


async def main():
    load_dotenv()

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Set GOOGLE_API_KEY in .env — see .env.example")
        return

    client = genai.Client(api_key=api_key)
    tools = get_tools(client)
    history: list[types.Content] = []

    print("Chat with the AI agent (type 'quit' to exit)\n")

    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            break

        if user_input.strip().lower() in ("quit", "exit"):
            break

        # Add user message
        history.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

        # Keep calling the model until it gives a text reply (not a tool call)
        while True:
            try:
                response = await client.aio.models.generate_content(
                    model=MODEL,
                    contents=history,
                    config=types.GenerateContentConfig(
                        tools=[tools],
                        system_instruction=SYSTEM_INSTRUCTION,
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                    ),
                )
            except Exception as e:
                print(f"\nError: {e}\n")
                break

            parts = response.candidates[0].content.parts
            tool_calls = [p for p in parts if p.function_call]

            if not tool_calls:
                # Final text answer
                text = "".join(p.text for p in parts if p.text)
                print(f"\nAgent: {text}\n")
                history.append(types.Content(role="model", parts=parts))
                break

            # Model wants to call tools — execute them and loop back
            history.append(types.Content(role="model", parts=parts))

            for part in tool_calls:
                fc = part.function_call
                print(f"  [tool] {fc.name}({dict(fc.args) if fc.args else {}})")
                result = await execute_tool(fc)
                history.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_function_response(name=fc.name, response={"result": result})],
                    )
                )


if __name__ == "__main__":
    asyncio.run(main())
