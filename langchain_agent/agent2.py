from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_community.document_loaders.csv_loader import CSVLoader
import pyttsx3



loader = CSVLoader(file_path="courses-report.2025-10-16.csv")
data = loader.load()

@tool
def query_course_data(query: str) -> str:
    """Iterates through data object and returns docs that match the query parameter"""
    results = []
    for doc in data:
        if query.lower() in doc.page_content.lower():
            results.append(doc.page_content)
    return "\n".join(results)

tools = [query_course_data]

model = ChatOllama(
    model="llama3.2:1b",
    temperature=0,
).bind_tools(tools)

messages = [
    SystemMessage(
        content="You are a helpful assistant whose name is Alfred. You help students at John Carroll University by answering questions on Math, Computer Science, and Data Science course information." \
        "ALWAYS use the tool provided to answer the user's question. ALWAYS use the user's input as the parameter for the tool." \
        "If you do not understand the question, ALWAYS answer with 'I do not understand the question, please ask again' and NEVER PROVIDE ANY OTHER INFORMATION." \
        "UNDER NO CIRCUMSTANCES should you ever answer questions that do not pertain to the course information." \
        "UNDER NO CIRCUMSTANCES should you ever use profanity." 

        "When you give an answer, respond in clear sentences, not in raw CSV text."

    ),
    HumanMessage(content="What is the course number for design patterns"),
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
                messages.append(
                    ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call["id"],
                        name=tool_name,
                    )
                )

                # Get final response after tool execution
                final_response = model.invoke(messages)
                final_response_content = final_response.content
                tools = response.tool_calls[0]["name"]
                print(f"Final response: {final_response.content}")
                print(f"Tools used: {tools}")


                engine = pyttsx3.init()
                engine.say(final_response_content)
                engine.runAndWait()   

                break
else:
    print("No tool calls were made.")