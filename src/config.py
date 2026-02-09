from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import logging

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Phase II and Phase III settings are combined in this single config.
    """

    # ============ Phase II Settings ============

    # Database
    database_url: str

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440

    # Auth
    better_auth_url: Optional[str] = None

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # ============ Phase III Settings ============

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    openai_max_tokens: int = 4096
    openai_temperature: float = 0.7

    # MCP
    enable_mcp: bool = False

    # AI Features
    enable_ai_chat: bool = False
    ai_stream_enabled: bool = True

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

    def validate_ai_config(self) -> list[str]:
        """
        Validate AI configuration and return list of warnings.

        Returns:
            List of warning messages (empty if all valid)
        """
        warnings = []

        if self.enable_ai_chat and not self.openai_api_key:
            warnings.append("⚠️  ENABLE_AI_CHAT is true but OPENAI_API_KEY is not set")

        if self.enable_ai_chat and not self.enable_mcp:
            warnings.append("⚠️  ENABLE_AI_CHAT is true but ENABLE_MCP is false")

        return warnings


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
