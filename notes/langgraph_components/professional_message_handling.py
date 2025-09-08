"""
When we are dealing with Chat Bots, one of the biggest challenges is to manage messages history in a way that
we keep context of the conversation, with reasonable llm costs.

To do so, we need a more professional method. This script shows how to do it.
"""
# Import libraries
from typing_extensions import Annotated, TypedDict, Literal

from IPython.display import Image, display
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END, add_messages, MessagesState
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, RemoveMessage

from codes.config.config import config


# Create ChatModel instance
llm = ChatGoogleGenerativeAI(
    model=config.model.model_name,
    api_key=config.model.api_key
)

# Create graph state
class State(MessagesState):
    summary: str


# Create Nodes
def llm_call(state: State):

    # Get summary if exists
    summary = state.get("summary", "")

    # If summary exists, then we add it to system message
    if summary:
        system_message = f"summary of conversation earlier: {summary}"
        messages = [SystemMessage(content=system_message)] + state["messages"]

    else:
        messages = state["messages"]


    response = llm.invoke(messages)
    return {"messages": response}


def summarize_conversation(state: State):

    # First, we get any existing summary
    summary = state.get("summary", "")

    # Create our summarization prompt
    if summary:
        # A summary already exists
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )

    else:
        summary_message = "Create a summary of the conversation above:"

    # Add prompt to our history
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = llm.invoke(messages)

    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}


# Create router
def router(state: State) -> Literal['summarize_conversation', 'END']:
    """Return the next node to execute."""

    # Check if there are any messages first
    if not state["messages"]:
        return "END"

    return "summarize_conversation" if len(state["messages"]) > 6 else "END"


workflow = StateGraph(State)

workflow.add_node("conversation", llm_call)
workflow.add_node("summarize_conversation", summarize_conversation)

workflow.add_edge(START, "conversation")
workflow.add_conditional_edges("conversation", router,
                               {
                                   "summarize_conversation": "summarize_conversation",
                                   "END": END
                               }
)
workflow.add_edge("summarize_conversation", END)

# Compile
graph = workflow.compile()
graph_image = graph.get_graph().draw_mermaid_png()
with open("chat_bot.png", "wb") as f:
    f.write(graph_image)
print("Graph saved as graph.png")


# For Studio
def get_graph():
    return graph
