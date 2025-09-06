"""
This is simple implementation of a re-act agent with LangGraph.

The intuition behind ReAct agent architecture is:
1- act: let the model call specific tool if needed.
2- observe: pass the output back to the model.
3- reason: decide what to do next (e.g., call another tool or just respond directly).
"""
# Import libraries
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import MessagesState, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver

from codes.config.config import config

# Create graph state with prebuilt MessageState
class GraphState(MessagesState):
    pass


# Create calculator tool
@tool("Multiply", description="Multiply two numbers")
def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b

@tool("add", description="Add two numbers")
def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b

@tool("divide", description="Divide two numbers")
def divide(a: int, b: int) -> float:
    """Divide a and b.

    Args:
        a: first int
        b: second int
    """
    return a / b


# Create ChatModel and bind tool
model = ChatGoogleGenerativeAI(model=config.model.model_name, api_key=config.model.api_key)
tools = [add, multiply, divide]
model_with_tool = model.bind_tools(tools, parallel_tool_calls=False)


# Create Node
def assistant_node(state: GraphState) -> GraphState:
    return {
        "messages": [model_with_tool.invoke(state["messages"])]
    }

# Build Graph
builder = StateGraph(GraphState)

builder.add_node("assistant", assistant_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition
)
builder.add_edge("tools", "assistant")

# Create memory and compile
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)


# For Studio
def get_graph():
    return graph

# Run the Graph
if __name__ == "__main__":

    # View the graph diagram
    graph_image = graph.get_graph().draw_mermaid_png()
    with open("simple_react_agent.png", "wb") as f:
        f.write(graph_image)
    print("Graph saved as graph.png")

    # Specify thread
    config = {"configurable": {"thread_id": "1"}}

    # First turn
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="Add 3 and 4.")
    ]
    result = graph.invoke({"messages": messages}, config=config)

    # Second turn
    messages.append(HumanMessage(content="Multiply the output by 2."))
    result2 = graph.invoke({"messages": messages}, config=config)

    for m in result2['messages']:
        m.pretty_print()
