from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")

    openai_azure_key: str = Field(default="", env="OPENAI_AZURE_KEY")
    openai_azure_base_url: str = Field(default="", env="OPENAI_AZURE_BASE_URL")
    openai_azure_api_version: str = Field(default="", env="OPENAI_AZURE_API_VERSION")

    open_ai_key: str = Field(default="", env="OPEN_AI_KEY")
    open_ai_url: str = Field(default="", env="OPEN_AI_URL")

    model_name: str = Field(default="gpt-5.2", env="MODEL_NAME")
    embedding_model_name: str = Field(
        default="text-embedding-3-small", env="EMBEDDING_MODEL_NAME"
    )

    # DEV
    vscode_extension_port: int = Field(default=0, env="VSCODE_EXTENSION_PORT")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
print(settings.model_dump_json(indent=2))
