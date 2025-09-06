"""
In Langchain ecosystem, always there are multiple ways to implement things.
For tools creation, there are mainly 3 methods to implement:
1. Use @tool decorator (Function-based).
2. Use StructuredTool.from_function (Class-based with schema).
3. Use BaseTool subclass (Custom class with full control).

Each has its own control level, below there is full description of each.
"""
# Import libraries
from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain_core.tools import tool, StructuredTool, BaseTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

######### Method 1: @tool decorator #########
"""
@tool decorator is the simplest way to create tools from functions.
It automatically infers tool name, description, and arguments from the function.
The function's docstring becomes the tool description - docstring is REQUIRED.
Best used for quick prototyping and simple tools.
"""


@tool
def calculator(expression: str) -> str:
    """Calculate mathematical expressions like '2+2' or '10*5'"""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"


@tool
def weather_checker(city: str) -> str:
    """Get current weather information for a city"""
    # Simulate API call
    weather_data = {
        "London": "Cloudy, 15°C",
        "New York": "Sunny, 22°C",
        "Tokyo": "Rainy, 18°C"
    }
    return weather_data.get(city, f"Weather data not available for {city}")


# Custom tool name and multi-parameter example
@tool("text_analyzer")
def analyze_text(text: str, analysis_type: str = "sentiment") -> str:
    """Analyze text for sentiment, length, or word count

    Args:
        text: The text to analyze
        analysis_type: Type of analysis - 'sentiment', 'length', or 'words'
    """
    if analysis_type == "sentiment":
        return f"Sentiment of '{text}': Positive"
    elif analysis_type == "length":
        return f"Length of text: {len(text)} characters"
    elif analysis_type == "words":
        return f"Word count: {len(text.split())} words"
    else:
        return "Unknown analysis type"


# Usage examples
calc_result = calculator.invoke({"expression": "15 * 3"})
weather_result = weather_checker.invoke({"city": "London"})
analysis_result = analyze_text.invoke({"text": "Hello world", "analysis_type": "words"})

print("@tool decorator results:")
print(f"Calculator: {calc_result}")
print(f"Weather: {weather_result}")
print(f"Analysis: {analysis_result}")

######### Method 2: StructuredTool.from_function #########
"""
StructuredTool.from_function provides more control over tool configuration.
You can specify custom names, descriptions, and argument schemas.
It supports both sync and async functions with detailed parameter validation.
Best used when you need more control than @tool decorator but less than BaseTool.
"""


def search_database(query: str, table: str, limit: int = 10) -> str:
    """Search database function - will be wrapped as a tool"""
    # Simulate database search
    return f"Found {limit} results for '{query}' in table '{table}'"


async def async_api_call(endpoint: str, method: str = "GET") -> str:
    """Async API call function"""
    # Simulate async API call
    return f"API call to {endpoint} using {method} method completed"


# Create structured tools with custom configuration
database_tool = StructuredTool.from_function(
    func=search_database,
    name="database_searcher",
    description="Search the company database for specific information",
    # You can add custom args_schema here if needed
)

# Async tool example
async_api_tool = StructuredTool.from_function(
    func=async_api_call,
    coroutine=async_api_call,  # Specify async version
    name="api_caller",
    description="Make asynchronous API calls to external services"
)


# Tool with custom return behavior
def critical_operation(operation: str) -> str:
    """Perform critical operations that should return directly to user"""
    return f"CRITICAL: {operation} completed successfully"


critical_tool = StructuredTool.from_function(
    func=critical_operation,
    name="critical_ops",
    description="Perform critical operations",
    return_direct=True  # Agent stops and returns result directly
)

# Usage examples
db_result = database_tool.invoke({"query": "user data", "table": "users", "limit": 5})
critical_result = critical_tool.invoke({"operation": "backup_database"})

print("\nStructuredTool.from_function results:")
print(f"Database: {db_result}")
print(f"Critical: {critical_result}")

######### Method 3: BaseTool subclass #########
"""
BaseTool subclass provides maximum control over tool implementation.
You can implement both sync (_run) and async (_arun) methods.
Supports custom error handling, callbacks, and complex validation logic.
Best used when you need complete control over tool behavior and lifecycle.
"""


class CalculatorInput(BaseModel):
    """Input schema for calculator tool"""
    first_number: float = Field(description="First number for calculation")
    second_number: float = Field(description="Second number for calculation")
    operation: str = Field(
        description="Mathematical operation: add, subtract, multiply, divide"
    )


class AdvancedCalculatorTool(BaseTool):
    """Advanced calculator with full error handling and validation"""

    name: str = "advanced_calculator"
    description: str = (
        "Perform mathematical operations with detailed error handling. "
        "Supports add, subtract, multiply, divide operations."
    )
    args_schema: Type[BaseModel] = CalculatorInput
    return_direct: bool = False

    def _run(
            self,
            first_number: float,
            second_number: float,
            operation: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the tool synchronously"""

        # Log tool usage if callback manager is provided
        if run_manager:
            run_manager.on_text(f"Calculating {first_number} {operation} {second_number}")

        try:
            if operation == "add":
                result = first_number + second_number
            elif operation == "subtract":
                result = first_number - second_number
            elif operation == "multiply":
                result = first_number * second_number
            elif operation == "divide":
                if second_number == 0:
                    return "Error: Division by zero is not allowed"
                result = first_number / second_number
            else:
                return f"Error: Unknown operation '{operation}'"

            return f"Result: {first_number} {operation} {second_number} = {result}"

        except Exception as e:
            return f"Calculation error: {str(e)}"

    async def _arun(
            self,
            first_number: float,
            second_number: float,
            operation: str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the tool asynchronously"""

        # For this example, async version is same as sync
        # In real scenarios, you might have async I/O operations
        return self._run(first_number, second_number, operation, None)


class FileManagerInput(BaseModel):
    """Input schema for file manager tool"""
    action: str = Field(description="Action to perform: read, write, delete, list")
    filename: str = Field(description="Name of the file to operate on")
    content: Optional[str] = Field(default=None, description="Content for write operations")


class FileManagerTool(BaseTool):
    """File management tool with comprehensive functionality"""

    name: str = "file_manager"
    description: str = (
        "Manage files in the system. Can read, write, delete, and list files. "
        "Use with caution as this can modify the file system."
    )
    args_schema: Type[BaseModel] = FileManagerInput

    def _run(
            self,
            action: str,
            filename: str,
            content: Optional[str] = None,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute file operations"""

        # Security check - only allow certain file types
        allowed_extensions = ['.txt', '.md', '.json', '.csv']
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            return f"Error: File type not allowed. Use: {', '.join(allowed_extensions)}"

        try:
            if action == "read":
                # Simulate file reading
                return f"Contents of {filename}: [File content would be here]"

            elif action == "write":
                if content is None:
                    return "Error: Content is required for write operations"
                # Simulate file writing
                return f"Successfully wrote {len(content)} characters to {filename}"

            elif action == "delete":
                # Simulate file deletion
                return f"Successfully deleted {filename}"

            elif action == "list":
                # Simulate directory listing
                return "Files in directory: file1.txt, file2.md, data.json"

            else:
                return f"Error: Unknown action '{action}'. Use: read, write, delete, list"

        except Exception as e:
            return f"File operation error: {str(e)}"

    async def _arun(
            self,
            action: str,
            filename: str,
            content: Optional[str] = None,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Async version of file operations"""
        # In real implementation, use async file I/O
        return self._run(action, filename, content, None)


# Create instances of custom tools
advanced_calc = AdvancedCalculatorTool()
file_manager = FileManagerTool()

# Usage examples
calc_result = advanced_calc.invoke({
    "first_number": 25,
    "second_number": 4,
    "operation": "multiply"
})

file_result = file_manager.invoke({
    "action": "write",
    "filename": "test.txt",
    "content": "Hello, World!"
})

print("\nBaseTool subclass results:")
print(f"Advanced Calculator: {calc_result}")
print(f"File Manager: {file_result}")

######### Tool Information and Schema Access #########
"""
All tools provide access to their metadata and schema information.
This is useful for debugging, documentation, and dynamic tool selection.
"""


def print_tool_info(tool, tool_name: str):
    """Helper function to print tool information"""
    print(f"\n{tool_name} Tool Info:")
    print(f"  Name: {tool.name}")
    print(f"  Description: {tool.description}")
    print(f"  Arguments Schema: {tool.args}")
    if hasattr(tool, 'return_direct'):
        print(f"  Return Direct: {tool.return_direct}")


# Print information for each tool type
print_tool_info(calculator, "@tool decorator")
print_tool_info(database_tool, "StructuredTool.from_function")
print_tool_info(advanced_calc, "BaseTool subclass")

######### Integration with Models #########
"""
All three tool types work identically when binding to language models.
The model sees the same interface regardless of implementation method.
"""

from langchain_openai import ChatOpenAI

# Create model and bind different tool types
model = ChatOpenAI(model="gpt-4")

# All tool types can be bound together
all_tools = [
    calculator,  # @tool decorator
    database_tool,  # StructuredTool.from_function
    advanced_calc,  # BaseTool subclass
    file_manager  # BaseTool subclass
]

model_with_tools = model.bind_tools(all_tools)

# The model can now use any of these tools
print("\nAll tools successfully bound to model!")
print(f"Model has access to {len(all_tools)} tools:")
for tool in all_tools:
    print(f"  - {tool.name}: {tool.description}")

######### Comparison Summary #########
"""
Method 1 (@tool decorator):
- Control Level: Low
- Complexity: Minimal
- Use Case: Quick prototyping, simple functions, minimal configuration

Method 2 (StructuredTool.from_function):
- Control Level: Medium  
- Complexity: Moderate
- Use Case: Custom configuration, async support, structured parameters

Method 3 (BaseTool subclass):
- Control Level: High
- Complexity: Advanced
- Use Case: Complex validation, custom error handling, full lifecycle control

Choose based on your needs:
- Simple functions → @tool decorator
- Custom configuration → StructuredTool.from_function
- Full control and validation → BaseTool subclass

All methods integrate identically with LangChain models and agents!
"""
