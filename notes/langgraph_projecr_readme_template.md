# Project Title
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.0-blue.svg?logo=langchain&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![Python](https://img.shields.io/badge/Python-3.9+-3776ab.svg?logo=python&logoColor=white)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991.svg?logo=openai&logoColor=white)](https://openai.com)
[![LangChain](https://img.shields.io/badge/LangChain-Enabled-1C3C3C.svg?logo=langchain&logoColor=white)](https://langchain.com)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg?logo=pytest&logoColor=white)](https://github.com/yourusername/project/actions)
[![Code Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen.svg?logo=codecov&logoColor=white)](https://codecov.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()
[![Contributors](https://img.shields.io/badge/Contributors-Welcome-orange.svg)](CONTRIBUTING.md)
[![Made with](https://img.shields.io/badge/Made%20with-❤️-red.svg)]()

>A concise, one-sentence description of your LangGraph project, focusing on its core functionality.

## Features

- **Feature1**: Description
- **Feature2**: Description  
- **Feature3**: Description

## Table of Contents

- [About](#about)
- [Workflow Diagram](#workflow-diagram)
- [Graph Overview](#graph-overview)
  - [State](#state)
  - [Nodes and Their Responsibilities](#nodes-and-their-responsibilities)
  - [Edges](#edges)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)
---
## About

Provide a detailed explanation of your project. What problem does this LangGraph workflow solve? Explain the logical flow from a user perspective, describing how the application processes input and generates an output. You can mention the role of the LangGraph framework in managing the complex, non-linear logic of the application.

---
## Workflow Diagram

A visual representation is crucial for understanding a LangGraph project. Insert a diagram of your graph here. You can generate one using tools like Mermaid or by exporting the graph from the LangChain platform.

![Workflow Diagram](codes/agent_with_search/agent_with_search.png)

Replace the above with a diagram of your actual workflow.

## State

The state object is the single source of truth for the entire graph. It is updated by each node as the graph progresses. Define the schema of your state object here:

```python
# Example state schema
from typing import TypedDict, List
from langgraph.graph import StateGraph

class GraphState(TypedDict):
    """Represents the state of our graph."""
    user_query: str
    intermediate_result: str
    final_output: str
```

Explain the purpose of each field in your state object.

## Nodes and Their Responsibilities

Each node in the graph is responsible for a specific task. Describe each node's role, what it reads from the state, and what it writes back.

### Node Name
A brief description of this node's function.

**Reads:**
- List of state variables this node reads.

**Writes:**
- List of state variables this node writes.

### Node 2 Name
A brief description of this node's function.

**Reads:**
- List of state variables this node reads.

**Writes:**
- List of state variables this node writes.

## Edges

Edges define the flow between nodes. Explain the routing logic, particularly for conditional edges, which are critical for dynamic behavior.

- **Edge Type (e.g., Simple Edge):** From Node A to Node B.
- **Edge Type (e.g., Conditional Edge):** From Node C to Node D or Node E.
  - **Condition:** Describe the logic that determines the next node. (e.g., "If the intermediate_result is 'complete', route to Node D, otherwise route to Node E.")

---
## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

- Python 3.9 or higher
- List any specific libraries (e.g., langchain, langgraph, openai)

### Installation

Clone the repository:

```bash
git clone https://github.com/your-username/your-project.git
cd your-project
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

Your LangGraph application uses a robust Pydantic-based configuration system with environment variable validation and cloud deployment support.

### Setup Environment Variables

1. **Copy the example configuration:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file with your actual values:**
   ```bash
   # See .env.example for complete list of required variables
   MODEL_API_KEY=sk-your-openai-api-key-here
   BOT_TOKEN=your-telegram-bot-token  
   NEWS_API_KEY=your-news-api-key
   DB_URI=mongodb://localhost:27017
   DB_NAME=crypto_news_db
   LANGSMITH_API_KEY=your-langsmith-api-key
   ```

### Configuration Structure

The system automatically validates and loads configuration using Pydantic:

```python
from src.config import config

# Access configuration values
print(f"Running {config.app_name} v{config.app_version}")
print(f"Environment: {config.environment}")
print(f"Debug mode: {config.debug}")

# Check environment
if config.is_production():
    # Production settings
    pass
elif config.is_development():
    # Development settings  
    pass
```

### Required Environment Variables

See [`.env.example`](.env.example) for the complete list of required environment variables and their descriptions. The configuration includes:

- **Application Settings**: Name, version, environment, debug mode
- **Database Configuration**: MongoDB connection URI and database name
- **LLM Configuration**: OpenAI model name and API key
- **Telegram Bot**: Bot token and group ID for notifications
- **News API**: API key and endpoint URL for crypto news
- **LangSmith**: Observability and tracing configuration (optional)

### Security Features

- **SecretStr fields** for sensitive data (API keys, tokens, URIs)
- **Validation on startup** - application exits if configuration is invalid  
- **GCP Secret Manager** support for cloud deployments
- **Environment-based loading** (.env for local, environment variables for production)
- **Strict validation** with Pydantic's `forbid` extra fields policy


### Error Handling

The configuration system provides detailed error messages for:
- Missing required environment variables
- Invalid value formats
- Type validation errors
- Database connection issues

If configuration validation fails, the application will exit with a clear error message indicating what needs to be fixed.

### Configuration Classes

The main configuration class structure:

```python
class SystemConfig(BaseSettings):
    # Application configurations
    app_name: str = "crypto-news-pipeline"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    # Database configurations
    db_uri: SecretStr
    db_name: str

    # LLM configurations
    model_name: str = "gpt-4o"
    model_api_key: SecretStr

    # Telegram configurations
    bot_token: SecretStr
    group_id: SecretStr

    # News API configurations
    news_api_key: SecretStr
    news_url: str

    # LangSmith configurations
    langchain_tracing_v2: bool = False
    langsmith_api_key: SecretStr
    langsmith_project: str = "crypto-news-pipeline"
```
---
## Usage

Provide a simple example of how to use the graph.

```python
# Example usage
from your_module import graph

inputs = {"user_query": "Tell me about the history of artificial intelligence."}
for step in graph.stream(inputs):
    print(step)
```
---
## Testing

Describe how to run the automated tests for this project.

```bash
# Example command to run tests
pytest
```
---
## Contributing

We welcome contributions! Please refer to our CONTRIBUTING.md for guidelines.

---
## License

This project is licensed under the [LICENSE NAME] - see the LICENSE.md file for details.

---
## Contact

- **Project Link:** [https://github.com/your-username/your-project](https://github.com/your-username/your-project)
- **Email:** [your-email@example.com](mailto:your-email@example.com)

---
## Acknowledgments

- List any individuals or resources you want to acknowledge.
- Credit the authors of any key third-party libraries.
