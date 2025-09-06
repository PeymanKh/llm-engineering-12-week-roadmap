"""
For ChatModel methods, there are mainly 6 core methods to enhance functionality:
1. with_structured_output() - For structured data responses.
2. bind_tools() - For function calling capabilities.
3. bind() - For parameter binding.
4. with_fallbacks() - For reliability and error handling.
5. with_retry() - For automatic retry logic.
6. with_config() - For monitoring and debugging.

Each has its own purpose and control level, below there is full description of each.
"""
# Import libraries
from typing import List
from pydantic import BaseModel, Field

from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


######### Method 1: with_structured_output() #########
"""
with_structured_output() ensures the model returns data in a specific structure.
This method guarantees format compliance and eliminates parsing errors.
Best used when you need reliable, structured responses from your model.
"""

class PersonInfo(BaseModel):
    name: str = Field(description="Person's full name")
    age: int = Field(description="Person's age in years")
    occupation: str = Field(description="Person's job title")
    location: str = Field(description="Person's city/country")

# Basic structured output usage
model1 = ChatOpenAI(model="gpt-4")
structured_model1 = model1.with_structured_output(PersonInfo)

# Usage - guaranteed to return PersonInfo object
response1 = structured_model1.invoke("Tell me about John, a 30-year-old teacher from London")
print("Structured Output:")
print(f"Name: {response1.name}, Age: {response1.age}")


######### Method 2: bind_tools() #########
"""
bind_tools() allows the model to call external functions and tools.
This enables the model to perform actions beyond just generating text.
Essential for building agents and interactive applications.
"""

@tool
def calculator(expression: str) -> str:
    """Perform mathematical calculations"""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except:
        return "Invalid expression"

@tool
def weather_checker(city: str) -> str:
    """Get weather information for a city"""
    # Simulated weather data
    weather_data = {
        "London": "Cloudy, 15°C",
        "New York": "Sunny, 22°C",
        "Tokyo": "Rainy, 18°C"
    }
    return weather_data.get(city, f"Weather data not available for {city}")

# Model with tools
model2 = ChatOpenAI(model="gpt-4")
model_with_tools = model2.bind_tools([calculator, weather_checker])

# Usage - model can call tools when needed
response2 = model_with_tools.invoke("What's 25 * 4 and what's the weather in London?")
print("Tools Response:")
print(response2)


######### Method 3: bind() #########
"""
bind() allows you to set fixed parameters for the model instance.
This method creates a new model with predefined settings like temperature, max_tokens.
Useful for creating specialized model variants for different tasks.
"""

# Different model personalities through parameter binding
creative_model = ChatOpenAI(model="gpt-4").bind(
    temperature=0.9,        # High creativity
    max_tokens=500,         # Longer responses
    frequency_penalty=0.2   # Encourage variety
)

analytical_model = ChatOpenAI(model="gpt-4").bind(
    temperature=0.1,        # Low creativity, more focused
    max_tokens=200,         # Shorter responses
    presence_penalty=0.1    # Encourage staying on topic
)

# Usage examples
creative_prompt = "Write a creative story about a robot"
analytical_prompt = "Analyze the benefits of renewable energy"

creative_response = creative_model.invoke(creative_prompt)
analytical_response = analytical_model.invoke(analytical_prompt)

print("Creative Model Response (high temp):")
print(creative_response.content[:100] + "...")


######### Method 4: with_fallbacks() #########
"""
with_fallbacks() adds backup models in case the primary model fails.
This method ensures your application remains functional even if one model is down.
Critical for production applications requiring high availability.
"""

# Primary model with Gemini as fallback
primary_model = ChatOpenAI(model="gpt-4")
gemini_fallback = ChatGoogleGenerativeAI(model="gemini-pro")
claude_fallback = ChatOpenAI(model="claude-3-sonnet")

model_with_fallbacks = primary_model.with_fallbacks([
    gemini_fallback,    # First fallback - Gemini
    claude_fallback     # Second fallback - Claude
])

# Usage - automatically tries fallbacks if primary fails
try:
    response4 = model_with_fallbacks.invoke("Explain quantum computing in simple terms")
    print("Fallback Model Response:")
    print(response4.content[:100] + "...")
except Exception as e:
    print(f"All models failed: {e}")


######### Method 5: with_retry() #########
"""
with_retry() adds automatic retry logic for failed requests.
This method handles temporary network issues or rate limiting.
Essential for robust applications that need to handle transient failures.
"""

# Model with retry configuration
retry_model = ChatOpenAI(model="gpt-4").with_retry(
    retry_config={
        "max_attempts": 3,      # Try 3 times total
        "initial_delay": 1,     # Wait 1 second before first retry
        "backoff_factor": 2,    # Double delay each retry
        "max_delay": 10         # Maximum delay between retries
    }
)

# Usage - automatically retries on failure
try:
    response5 = retry_model.invoke("What are the latest AI developments?")
    print("Retry Model Response:")
    print(response5.content[:100] + "...")
except Exception as e:
    print(f"Failed after retries: {e}")


######### Method 6: with_config() #########
"""
with_config() adds runtime configuration like tags, metadata, and callbacks.
This method is essential for monitoring, debugging, and tracking model usage.
Useful for production applications requiring observability.
"""

# Model with comprehensive configuration
configured_model = ChatOpenAI(model="gpt-4").with_config(
    tags=["production", "chatbot", "customer-service"],
    metadata={
        "user_id": "user_123",
        "session_id": "session_456",
        "app_version": "1.2.3",
        "environment": "production"
    }
)

# Usage - includes tracking information
response6 = configured_model.invoke("How can I improve my Python skills?")
print("Configured Model Response:")
print(response6.content[:100] + "...")


######### Advanced: Method Chaining #########
"""
The real power comes from chaining multiple methods together.
This creates highly robust, feature-rich model instances.
Combines all benefits: structure, tools, reliability, monitoring.
"""

class TaskResponse(BaseModel):
    task_type: str = Field(description="Type of task being performed")
    result: str = Field(description="Result or answer")
    confidence: float = Field(description="Confidence level 0-1")
    tools_used: List[str] = Field(description="List of tools that were used")

# Ultimate enhanced model with all methods chained
ultimate_model = (ChatOpenAI(model="gpt-4")
    .bind_tools([calculator, weather_checker])              # Add tools
    .bind(temperature=0.7, max_tokens=1000)                # Set parameters
    .with_structured_output(TaskResponse)                   # Structure output
    .with_retry()                                          # Add retry logic
    .with_fallbacks([ChatGoogleGenerativeAI(model="gemini-pro")])  # Gemini fallback
    .with_config(                                          # Add monitoring
        tags=["ultimate", "production"],
        metadata={"model_type": "enhanced_chatgpt"}
    )
)

# Usage of ultimate model
ultimate_response = ultimate_model.invoke(
    "Calculate 15 * 23, check weather in Tokyo, and summarize the results"
)

print("Ultimate Model Response:")
print(f"Task Type: {ultimate_response.task_type}")
print(f"Result: {ultimate_response.result}")
print(f"Confidence: {ultimate_response.confidence}")
print(f"Tools Used: {ultimate_response.tools_used}")


######### Comparison Summary #########
"""
Method 1 (with_structured_output): Guaranteed structured responses, eliminates parsing
Method 2 (bind_tools): Function calling, enables agents and interactive features  
Method 3 (bind): Parameter control, create specialized model variants
Method 4 (with_fallbacks): High availability, handles model failures
Method 5 (with_retry): Handles transient failures, improves reliability
Method 6 (with_config): Monitoring and debugging, production observability

Choose based on your needs:
- Need structured data → with_structured_output()
- Need function calling → bind_tools()  
- Need parameter control → bind()
- Need reliability → with_fallbacks() + with_retry()
- Need monitoring → with_config()
- Need everything → Chain them all together!
"""
