"""
Configuration Management
========================

Centralized configuration management for the ticket sales agent system.
"""

import os
from typing import Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    
    # Weaviate settings
    weaviate_url: str = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    weaviate_api_key: str = os.getenv("WEAVIATE_API_KEY", "")
    
    # Neo4j settings
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_username: str = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "")


@dataclass
class VAPIConfig:
    """VAPI configuration settings."""
    
    api_key: str = os.getenv("VAPI_API_KEY", "")
    base_url: str = os.getenv("VAPI_BASE_URL", "https://api.vapi.ai")
    default_voice: str = "alloy"
    max_call_duration: int = 300  # 5 minutes
    recording_enabled: bool = True


@dataclass
class OpenAIConfig:
    """OpenAI configuration settings."""
    
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = "gpt-4o-realtime-preview"
    temperature: float = 0.7
    max_tokens: int = 300


@dataclass
class MCPConfig:
    """MCP Server configuration settings."""
    
    host: str = os.getenv("MCP_SERVER_HOST", "localhost")
    port: int = int(os.getenv("MCP_SERVER_PORT", "8000"))


@dataclass
class AppConfig:
    """Application configuration settings."""
    
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    environment: str = os.getenv("ENVIRONMENT", "development")
    max_concurrent_calls: int = 10
    call_retry_attempts: int = 3
    call_retry_delay: int = 5  # seconds


class ConfigManager:
    """Centralized configuration manager."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self.database = DatabaseConfig()
        self.vapi = VAPIConfig()
        self.openai = OpenAIConfig()
        self.mcp = MCPConfig()
        self.app = AppConfig()
        
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration values."""
        required_configs = {
            "VAPI_API_KEY": self.vapi.api_key,
            "OPENAI_API_KEY": self.openai.api_key,
            "NEO4J_PASSWORD": self.database.neo4j_password
        }
        
        missing_configs = [key for key, value in required_configs.items() if not value]
        
        if missing_configs:
            raise ValueError(f"Missing required configuration: {', '.join(missing_configs)}")
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration."""
        return self.database
    
    def get_vapi_config(self) -> VAPIConfig:
        """Get VAPI configuration."""
        return self.vapi
    
    def get_openai_config(self) -> OpenAIConfig:
        """Get OpenAI configuration."""
        return self.openai
    
    def get_mcp_config(self) -> MCPConfig:
        """Get MCP configuration."""
        return self.mcp
    
    def get_app_config(self) -> AppConfig:
        """Get application configuration."""
        return self.app
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)."""
        return {
            "database": {
                "weaviate_url": self.database.weaviate_url,
                "neo4j_uri": self.database.neo4j_uri,
                "neo4j_username": self.database.neo4j_username
            },
            "vapi": {
                "base_url": self.vapi.base_url,
                "default_voice": self.vapi.default_voice,
                "max_call_duration": self.vapi.max_call_duration,
                "recording_enabled": self.vapi.recording_enabled
            },
            "openai": {
                "model": self.openai.model,
                "temperature": self.openai.temperature,
                "max_tokens": self.openai.max_tokens
            },
            "mcp": {
                "host": self.mcp.host,
                "port": self.mcp.port
            },
            "app": {
                "log_level": self.app.log_level,
                "environment": self.app.environment,
                "max_concurrent_calls": self.app.max_concurrent_calls
            }
        }


# Global configuration instance
config = ConfigManager()
