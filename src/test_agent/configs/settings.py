from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    openrouter_api_key: str
    tavily_api_key: str
    langfuse_public_key: str
    langfuse_secret_key: str

    openrouter_model: str = Field(default="z-ai/glm-5.2")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1")

    langfuse_host: str = Field(default="http://127.0.0.1:3000")

    a2a_host: str = Field(default="127.0.0.1")
    a2a_port: int = Field(default=9000)


settings = Settings()
