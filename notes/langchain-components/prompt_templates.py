"""
In Langchain, there are multiple types of prompt templates for different use cases.
For prompt templates, there are mainly 5 different types:
1. Basic Prompt Templates (String-based).
2. Chat Prompt Templates (Multi-role conversations).
3. Few-shot Prompt Templates (Example-based learning).
4. Dynamic Prompt Templates (Context-aware prompts).
5. Conditional Prompt Templates (Logic-driven prompts).

Each serves different purposes and scenarios, below there is full description of each.
"""
# Import libraries
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, FewShotPromptTemplate


######### Type 1: Basic Prompt Templates #########
"""
Basic Prompt Templates are simple string-based templates with placeholders.
They are ideal for single-turn interactions and straightforward text generation tasks.
Best used with completion models or simple question-answering scenarios.
"""

# Simple template with one variable
basic_template1 = PromptTemplate(
    input_variables=["topic"],
    template="Write a short poem about {topic}."
)

# Template with multiple variables
basic_template2 = PromptTemplate(
    input_variables=["style", "subject", "length"],
    template="""
Write a {length} {style} about {subject}.
Make it engaging and informative.
"""
)

# Usage examples
poem_prompt = basic_template1.format(topic="autumn")
article_prompt = basic_template2.format(
    style="blog post",
    subject="machine learning",
    length="medium-length"
)

print("Basic Template Output:")
print(article_prompt)


######### Type 2: Chat Prompt Templates #########
"""
Chat Prompt Templates handle multi-role conversations with system, user, and assistant messages.
They are perfect for chat models and complex conversational AI applications.
Support different message roles and conversation context.
"""

# Advanced chat template with conversation history
chat_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert {role}. Always provide detailed explanations."),
    ("human", "{input}"),
    ("ai", "I'll help you with that. Let me think about {input} step by step."),
    ("human", "Please continue with more details.")
])

chat_messages = chat_template.format_messages(
    role="data scientist",
    input="what is the best way to learn python?",
)

print("\nChat Template Output:")
for msg in chat_messages:
    print(f"{msg.__class__.__name__}: {msg.content}")


######### Type 3: Few-shot Prompt Templates #########
"""
Few-shot Prompt Templates provide examples to guide model behavior.
They are excellent for teaching specific formats, styles, or reasoning patterns.
Help models understand desired output structure through examples.
"""

# Define examples for few-shot learning
examples = [
    {
        "question": "What is the capital of France?",
        "answer": "The capital of France is Paris. It is located in the Île-de-France region and serves as the country's political, economic, and cultural center."
    },
    {
        "question": "What is photosynthesis?",
        "answer": "Photosynthesis is the process by which plants convert sunlight, carbon dioxide, and water into glucose and oxygen. This process occurs mainly in the chloroplasts of plant cells."
    },
    {
        "question": "Who invented the telephone?",
        "answer": "Alexander Graham Bell is credited with inventing the telephone in 1876. He received the first U.S. patent for the invention of the telephone."
    }
]

# Create example template
example_template = PromptTemplate(
    input_variables=["question", "answer"],
    template="Question: {question}\nAnswer: {answer}"
)

# Create few-shot template
few_shot_template = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_template,
    prefix="You are an educational assistant. Provide detailed, accurate answers following these examples:",
    suffix="Question: {input}\nAnswer:",
    input_variables=["input"]
)

few_shot_prompt = few_shot_template.format(input="What is machine learning?")
print("\nFew-shot Template Output:")
print(few_shot_prompt)