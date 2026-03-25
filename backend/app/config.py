from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")

    azure_openai_key: str = Field(default="", env="AZURE_OPENAI_KEY")
    azure_openai_base_url: str = Field(default="", env="AZURE_OPENAI_BASE_URL")
    azure_api_version: str = Field(default="", env="AZURE_API_VERSION")

    openai_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_base_url: str = Field(default="", env="OPENAI_BASE_URL")

    openai_model_name: str = Field(default="gpt-5.2", env="OPENAI_MODEL_NAME")
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
