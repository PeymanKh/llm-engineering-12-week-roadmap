"""
Configuration Management Module

Handles secure loading and validation of environment variables with support
for local .env files and cloud deployment with GCP Secret Manager integration.

Environment Variables Format:
    - Simple settings: APP_NAME, ENVIRONMENT, DEBUG
    - Nested settings: GCP__PROJECT_ID, DATABASE__URI, MODEL__API_KEY
    - Read .env.example for more information

Usage:
    from config.config import config

    if config.is_production():
        # Production-specific logic
        pass
"""
# Import libraries
import sys
import logging
from enum import Enum
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import SecretStr, Field, ValidationError, BaseModel

from codes.utils.helpers import get_default_host


class LogLevel(str, Enum):
    """Standard logging levels for application logging configuration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LLMProvider(str, Enum):
    """Supported Large Language Model providers."""
    OPENAI = "openai"
    GOOGLE = "google"


class DatabaseConfig(BaseModel):
    """
    Database connection configuration.

    Attributes:
        uri: Database connection string (MongoDB format recommended)
        name: Database name for the application
    """
    uri: SecretStr = Field(
        description="MongoDB connection URI"
    )
    name: str = Field(
        default="llmEngineering12Week",
        description="Database name"
    )


class ModelConfig(BaseModel):
    """
    Large Language Model provider configuration.

    Attributes:
        provider: LLM provider (openai or google)
        model_name: LLM model identifier (e.g., gpt-4o, gemini-2.5-flash)
        api_key: Provider API key for authentication
        temperature: Model temperature (range: 0.0 - 1.0)
    """
    provider: LLMProvider = Field(
        default=LLMProvider.GOOGLE,
        description="LLM provider"
    )
    model_name: str = Field(
        default="gemini-2.5-flash",
        description="LLM model identifier"
    )
    api_key: SecretStr = Field(
        description="LLM provider API key"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Model temperature"
    )


class SystemConfig(BaseSettings):
    """
    Main application configuration with environment-based loading.

    Supports local development with .env files and cloud deployment
    with environment variables from GCP Secret Manager.

    Read .env.example for more information about Environment Variables
    """

    # Application Settings with defaults
    app_name: str = Field(
        default="llm-engineering-12-week",
        description="Application identifier"
    )
    app_description: str = Field(
        default="LLM Engineering 12 Week Challenge",
        description="Application description"
    )
    app_version: str = Field(
        default="1.0.0",
        description="Application version"
    )
    app_author: str = Field(
        default="Peyman Khodabandehlouei",
        description="Application author"
    )
    environment: str = Field(
        default="development",
        description="Deployment environment"
    )
    debug: bool = Field(
        default=True,
        description="Enable debug mode"
    )

    # Server Configuration with defaults
    host: str = Field(
        default_factory=get_default_host,
        description="Server bind address"
    )
    port: int = Field(
        default=8080,
        ge=1,
        le=65535,
        description="Server port"
    )

    # Logging Configuration with defaults
    log_level: LogLevel = Field(
        default=LogLevel.DEBUG,
        description="Logging level"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format string"
    )

    langsmith_project: str = Field(
        ...,
        description="LangSmith project name"
    )
    langsmith_api_key: str = Field(
        ...,
        description="LangSmith API key"
    )
    langchain_tracing_v2: bool = Field(
        default=True,
        description="Langsmith Tracing"
    )

    tavily_api_key: SecretStr = Field(
        ...,
        description="Tavily API key"
    )


    # External Service Configurations
    database: DatabaseConfig
    model: ModelConfig

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    def is_openai_provider(self) -> bool:
        """Check if using OpenAI as LLM provider."""
        return self.model.provider == LLMProvider.OPENAI

    def is_google_provider(self) -> bool:
        """Check if using Google as LLM provider."""
        return self.model.provider == LLMProvider.GOOGLE

    class Config:
        """Pydantic configuration for environment variable loading."""
        env_file = Path(__file__).parent.parent.parent / '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
        env_nested_delimiter = '__'


# Initialize logging with basic configuration
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=DEFAULT_LOG_FORMAT)

# Load and validate configuration on module import
try:
    config = SystemConfig()
    logging.info(f"Configuration loaded for environment: {config.environment}")
except ValidationError as e:
    logging.error(f"Configuration validation failed: {e}")
    sys.exit(1)
except Exception as e:
    logging.error(f"Failed to load configuration: {e}")
    sys.exit(1)


# Public API
__all__ = ['config', 'SystemConfig']
