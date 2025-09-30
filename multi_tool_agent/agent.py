from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

#This is where we define the function that will act as our tool
#def get_current_time(city):
    # Your logic to get time from a city timezone
#    pass
    
#tools=[get_current_time]


root_agent = Agent(
    model=LiteLlm(model="ollama_chat/llama3.2:1b"),
    name="Alfred",
    description=(
        "You are a simple agent that likes to converse with users"
    ),
    instruction="""
      Respond accordingly to user input in a friendly way.
    """,
    tools=[],
)