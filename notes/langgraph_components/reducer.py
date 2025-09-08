"""
In LangGraph, reducer is a function that defines how the graph's state should be updated when a node produces
output.

Each state key can have a reducer function, a reducer takes the previous value and the new value and returns
the updated value. without reducer, the new value would just overwrite the old one.
With a reducer, we can define accumulation, merging, or more complex logic.

When we define the state, we can Annotate the reducer function we want.
"""
# Import libraries
import operator
from typing import TypedDict
from typing_extensions import Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages  # Built-in reducer in langgraph


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    score: Annotated[int, lambda prev, new: prev + new]

"""
Also we can use builtin operator library to create Annotated fields in our graph state
"""
class CustomState(TypedDict):
    foo: Annotated[list[int], operator.add]

"""
In LangGraph, there exists a prebuilt state called `MessageState` which makes it easy to use messages.
It is defined with a single messages key which is a list of AnyMessage objects and uses the add_messages reducer.
"""
from langgraph.graph import MessagesState

class GraphState(MessagesState):
    documents: list[str]



"""
Custom Reducers
"""
def reduce_list(left: list | None, right: list | None) -> list:
    """Safely combine two lists, handling cases where either or both inputs might be None.

    Args:
        left (list | None): The first list to combine, or None.
        right (list | None): The second list to combine, or None.

    Returns:
        list: A new list containing all elements from both input lists.
               If an input is None, it's treated as an empty list.
    """
    if not left:
        left = []
    if not right:
        right = []
    return left + right


class CustomReducerState(TypedDict):
    foo: Annotated[list[int], reduce_list]
