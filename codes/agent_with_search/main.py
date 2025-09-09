"""
This script implements an agent capable of web search with Tavily and access Wikipedia
to answer user queries.
"""
# Import libraries
from operator import add
from typing_extensions import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_community.tools import TavilySearchResults
from langchain_community.document_loaders import WikipediaLoader

from codes.config.config import config

# Create ChatModel
llm = ChatGoogleGenerativeAI(
    model=config.model.model_name,
    api_key=config.model.api_key
)

# Create State
class State(TypedDict):
    question: str
    answer: str
    context: Annotated[list, add]

# Create Nodes
def search_web(state):
    """ Retrieve docs from web search """

    # Search
    tavily_search = TavilySearchResults(tavily_api_key=config.tavily_api_key.get_secret_value(), max_results=3)
    search_docs = tavily_search.invoke(state['question'])

    # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}">\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}


def search_wikipedia(state):
    """ Retrieve docs from wikipedia """

    # Search
    search_docs = WikipediaLoader(query=state['question'],
                                  load_max_docs=2).load()

    # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}">\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}


def generate_answer(state):
    """ Node to answer a question """

    # Get state
    context = state["context"]
    question = state["question"]

    # Template
    answer_template = """Answer the question {question} using this context: {context}"""
    answer_instructions = answer_template.format(question=question,
                                                 context=context)

    # Answer
    answer = llm.invoke([SystemMessage(content=answer_instructions)] + [HumanMessage(content=f"Answer the question.")])

    # Append it to state
    return {"answer": answer}


# Add nodes
builder = StateGraph(State)

# Initialize each node with node_secret
builder.add_node("search_web",search_web)
builder.add_node("search_wikipedia", search_wikipedia)
builder.add_node("generate_answer", generate_answer)

# Flow
builder.add_edge(START, "search_wikipedia")
builder.add_edge(START, "search_web")
builder.add_edge("search_wikipedia", "generate_answer")
builder.add_edge("search_web", "generate_answer")
builder.add_edge("generate_answer", END)
graph = builder.compile()

graph_image = graph.get_graph().draw_mermaid_png()
with open("agent_with_search.png", "wb") as f:
    f.write(graph_image)


result = graph.invoke({"question": "What is the latest price for bitcoin?"})
print(result['answer'].content)