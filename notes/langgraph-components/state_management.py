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
