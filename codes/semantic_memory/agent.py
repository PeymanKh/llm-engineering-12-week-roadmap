# Import libraries
import uuid
from typing import List, Optional
from pydantic import BaseModel, Field

from trustcall import create_extractor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage

from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END, MessagesState

from codes.config.config import config

# Initialize LLM
llm = ChatOpenAI(api_key=config.openai_api_key.get_secret_value(), model="gpt-4o")


# Long-Term memory schema
class UserProfile(BaseModel):
    name: Optional[str] = Field(
        None,
        description="The name of the user."
    )
    gender: Optional[str] = Field(
        None,
        description="The gender of the user."
    )
    age: Optional[int] = Field(
        None,
        description="The age of the user."
    )
    interests: Optional[List[str]] = Field(
        None,
        description="The user's interests."
    )
    preferences: Optional[List[str]] = Field(
        None,
        description="The user's preferences."
    )


# Prompts
assistant_system_message = PromptTemplate(
    input_variables=["memory"],
    template="""You are a helpful assistant with a memory that provides information about the user.
Use this memory to personalize your responses. here is memory for this user (can be empty):
```{memory}```)"""
)

update_memory_prompt = PromptTemplate(
    input_variables=["memory"],
    template="""You are memory updater. The information about user is as follow:
```{memory}```

Based on chathistory below, update the memory and expand it if new information is available."""
)


# Nodes
def assistant(state: MessagesState, config: RunnableConfig, store: BaseStore):
    """This node is responsible for responding to the user's question."""
    user_id = config["configurable"]["user_id"]

    # Retrieve the memory for the user
    namespace = ("memory", user_id)
    key = "user_profile"
    existing_memory = store.get(namespace, key)

    if existing_memory:
        existing_memory_content = existing_memory.value
    else:
        existing_memory_content = "No memory available."

    # Create a prompt for the assistant
    system_prompt = assistant_system_message.format(memory=existing_memory_content)

    # Invoke the LLM
    response = llm.invoke([SystemMessage(content=system_prompt)] + state["messages"])
    print(existing_memory_content)
    return {"messages": [response]}


def update_memory(state: MessagesState, config: RunnableConfig, store: BaseStore):
    """This node is responsible for updating the user's memory."""
    user_id = config["configurable"]["user_id"]

    # Retrieve the memory for the user
    namespace = ("memory", user_id)
    key = "user_profile"
    existing_memory = store.get(namespace, key)

    if existing_memory:
        existing_memory_content = existing_memory.value
    else:
        existing_memory_content = "No memory available."

    # Create a prompt for the memory updater
    system_prompt = update_memory_prompt.format(memory=existing_memory_content)

    # Add output structure to the LLM
    llm_with_structure = llm.with_structured_output(UserProfile)

    # Invoke the LLM
    response = llm_with_structure.invoke([SystemMessage(content=system_prompt)] + state["messages"])

    # Store the updated memory in the store
    store.put(namespace, key, response)


# Build graph
builder = StateGraph(MessagesState)

builder.add_node("assistant", assistant)
builder.add_node("update_memory", update_memory)

builder.add_edge(START, "assistant")
builder.add_edge("assistant", "update_memory")
builder.add_edge("update_memory", END)


def main():
    """Main CLI function for the semantic memory agent."""

    # Initialize the checkpointer for short-term memory
    memory = InMemorySaver()

    # Initialize the store for long-term memory
    store = InMemoryStore()

    # Generate a user ID for this session
    user_id = str(uuid.uuid4())

    # Configure the graph
    config_dict = {"configurable": {"thread_id": "test-1", "user_id": user_id}}

    # Compile the graph
    graph = builder.compile(checkpointer=memory, store=store)

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        human_message = HumanMessage(content=user_input)

        result = graph.invoke({"messages": [human_message]}, config=config_dict)

        messages = result["messages"]

        print("Assistant:", messages[-1].content)



if __name__ == "__main__":
    main()