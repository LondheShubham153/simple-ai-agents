"""Simple Bedrock AI agent with tool calling (manual loop, like the Gemini agent).

Run:  python agent.py
Needs: AWS credentials configured (via env vars, ~/.aws/credentials, or SSO)
"""

import boto3

from tools import TOOL_CONFIG, execute_tool

SYSTEM_PROMPT = (
    "You are a helpful agent that can use tools to answer questions. "
    "If no tools are needed, respond in haikus."
)
MODEL = "us.anthropic.claude-sonnet-4-20250514-v1:0"


def main():
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    history: list[dict] = []

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

        history.append({"role": "user", "content": [{"text": user_input}]})

        # Keep calling the model until it gives a text reply (not a tool call)
        while True:
            try:
                response = client.converse(
                    modelId=MODEL,
                    messages=history,
                    system=[{"text": SYSTEM_PROMPT}],
                    toolConfig=TOOL_CONFIG,
                )
            except Exception as e:
                print(f"\nError: {e}\n")
                break

            output_msg = response["output"]["message"]
            history.append(output_msg)

            if response["stopReason"] != "tool_use":
                # Final text answer
                text = "".join(
                    block["text"] for block in output_msg["content"] if "text" in block
                )
                print(f"\nAgent: {text}\n")
                break

            # Model wants to call tools — execute them and loop back
            tool_results = []
            for block in output_msg["content"]:
                if "toolUse" not in block:
                    continue
                tool = block["toolUse"]
                print(f"  [tool] {tool['name']}({tool['input']})")
                try:
                    result = execute_tool(tool["name"], tool["input"])
                    tool_results.append(
                        {"toolResult": {"toolUseId": tool["toolUseId"], "content": [{"text": result}]}}
                    )
                except Exception as e:
                    tool_results.append(
                        {"toolResult": {"toolUseId": tool["toolUseId"], "content": [{"text": str(e)}], "status": "error"}}
                    )

            history.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    main()
