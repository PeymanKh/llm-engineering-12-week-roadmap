"""
In Langchain ecosystem, always there are multiple ways to implement things.
for state of the graph, there are mainly 3 methods to implement:
1. Use a TypeDict.
2. Use a DataClass.
3. Use Pydantic's BaseModel.

Each has its own control level, below there is full description of each.
"""
# Import libraries
from dataclasses import dataclass
from typing import TypedDict, Literal
from pydantic import BaseModel, ValidationError


######### Method 1: TypeDict #########
"""
TypeDict allows us to define dictionary types with specific expected keys and value types.

TypeDict is actually a TypeHint, It means python does NOT enforce this type while running, 
They are only suggested for developers and IDE to understand the code better before runtime.
"""

class TypeDictState(TypedDict):
    name: str
    age: int
    gender: Literal["male", "female"]

state1 = TypeDictState(name="Peyman", age=20, gender="male")
state2 = TypeDictState(name=20.5, age="Hi", gender="cat")  # This one has wrong types, but no error happens

state1['name'] = "Nomad!"  # How we edit


######### Method 2: DataClass #########
"""
Same as TypeDict, The difference is on definition and how we change the values.
"""
@dataclass
class DataClassState:
    name: str
    age: int
    gender: Literal["male", "female"]

state3 = DataClassState(name="Peyman", age=20, gender="male")

state3.name = "Nomad!"


######### Method 3: BaseModel #########
"""
Pydantic is a data validation and settings management library. It can perform validations to 
check whether data is same as specified types and constraints.
"""

class PydanticState(BaseModel):
    name: str
    age: int
    gender: Literal["male", "female"]

    # This method is for custom validation, can be skipped....
    @classmethod
    def validate_name(cls, value):
        if value not in ["male", "femail"]:
            raise ValidationError("Each gender must be either 'male' or 'femail'")

try:
    state5 = PydanticState(name="Peyman", age=20, gender="meaw")
except ValidationError as e:
    print("Validation Error:", e)


"""
Multiple Schemas:

In some cases. out nodes might communicate internally, and those schemas doesn't need to be included
in our main schema which contains input and output of the graph. In such case, we can use multiple
schemas.
"""
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class OverallState(TypedDict):
    foo: int

class PrivateState(TypedDict):
    baz: int

def node_1(state: OverallState) -> PrivateState:
    print("---Node 1---")
    return {"baz": state['foo'] + 1}

def node_2(state: PrivateState) -> OverallState:
    print("---Node 2---")
    return {"foo": state['baz'] + 1}

# Build graph
builder = StateGraph(OverallState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)

# Logic
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_2", END)

# Add
graph = builder.compile()


"""
We can also define different states for input and output as follow:
"""
class InputState(TypedDict):
    question: str


class OutputState(TypedDict):
    answer: str


class OverallState(TypedDict):
    question: str
    answer: str
    notes: str


def thinking_node(state: InputState):
    return {"answer": "bye", "notes": "... his is name is Lance"}


def answer_node(state: OverallState) -> OutputState:
    return {"answer": "bye Lance"}


graph1 = StateGraph(OverallState, input_schema=InputState, output_schema=OutputState)
graph1.add_node("answer_node", answer_node)
graph1.add_node("thinking_node", thinking_node)
graph1.add_edge(START, "thinking_node")
graph1.add_edge("thinking_node", "answer_node")
graph1.add_edge("answer_node", END)

graph3 = graph1.compile()

graph.invoke({"question":"hi"})

