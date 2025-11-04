from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

@tool
def add(x: int, y: int) -> int:
    """Adds 2 numbers and returns the result"""
    return x + y

tools = [add]

model = ChatOllama(
    model="llama3.2:1b",
    temperature=0,
).bind_tools(tools)

messages = [
    SystemMessage(
        content="You are a helpful assistant, always use the tools provided to answer the user's question."
    ),
    HumanMessage(content="use the add tool to add 2 + 2"),
]

# First model call - will likely get a tool call
response = model.invoke(messages)
print(f"Initial response: {response}")

# Check for tool calls
if response.tool_calls:
    # Loop through each tool call
    for tool_call in response.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]

        # Find the matching tool
        for tool in tools:
            if tool.name == tool_name:
                # Execute the tool with the arguments
                tool_result = tool.invoke(tool_args)
                print(f"Tool result: {tool_result}")

                # Add the tool result to the messages
                messages.append(response)
                messages.append(
                    ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_id,
                        name=tool_name,
                    )
                )

                # Get final response after tool execution
                final_response = model.invoke(messages)
                print(f"Final response: {final_response.content}")
                break
else:
    print("No tool calls were made.")