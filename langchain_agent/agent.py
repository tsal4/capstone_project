from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool

#FIRST AGENT (NOT USED)

'''
#example tool
@tool
def validate_user(user_id: int, addresses: str) -> bool:
    """Validate user using historical addresses.

    Args:
        user_id (int): the user ID.
        addresses (str): Previous addresses as a list of strings.
    """
    return True
'''

llm = ChatOllama(
    model="llama3.2:1b",
    temperature=0,
)
#.bind_tools([validate_user])

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a friendly assistant that only says hello to any user input.",
        ),
        ("human", "{input}"),
    ]
)

chain = prompt | llm
result = chain.invoke(
    {
        "input_language": "English",
        "output_language": "English",
        "input": "How are you doing",
    }
)

print(result.content)