"""
When we are building Chat Bots, we need to manage messages to keep the costs optimized.

In langgraph, there are mainly 3 ways to do this:
1- is to have a filter node to only keep desired number of messages in state and remove the rest.
2- we can only pass the last message to llm while we invoke.
3- we can trim the history based on tokens of message history.
"""
# Import libraries
from langchain_openai import ChatOpenAI
from langchain_core.messages import RemoveMessage, trim_messages
from langgraph.graph import MessagesState, StateGraph, START, END

llm = ChatOpenAI()


####### Method 1: Reduce #######
# Nodes
def filter_messages(state: MessagesState):
    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"messages": delete_messages}

def chat_model_node(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"])]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("filter", filter_messages)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "filter")
builder.add_edge("filter", "chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()


####### Method 2: Filter #######
# Node
def chat_model_node(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"][-1:])]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)
graph2 = builder.compile()


####### Method 3: Trim #######

# Node
def chat_model_node(state: MessagesState):
    messages = trim_messages(
            state["messages"],
            max_tokens=100,
            strategy="last",
            token_counter=ChatOpenAI(model="gpt-4o"),
            allow_partial=False,
        )
    return {"messages": [llm.invoke(messages)]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)
graph3 = builder.compile()


