from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    app_name: str = "Leadership Insights Agent"
    app_version: str = "0.1.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # File Upload
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "./uploads"

    azure_openai_key: str = Field(default="", env="AZURE_OPENAI_KEY")
    azure_openai_base_url: str = Field(default="", env="AZURE_OPENAI_BASE_URL")
    azure_api_version: str = Field(default="", env="AZURE_API_VERSION")
    openai_model_name: str = Field(default="", env="OPENAI_MODEL_NAME")
    embedding_model_name: str = Field(default="", env="EMBEDDING_MODEL_NAME")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
