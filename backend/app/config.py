# from pydantic_settings import BaseSettings


# class Settings(BaseSettings):
#     """Application settings."""

#     # API Configuration
#     app_name: str = "Leadership Insights Agent"
#     app_version: str = "0.1.0"
#     api_host: str = "0.0.0.0"
#     api_port: int = 8000

#     # CORS
#     allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

#     # File Upload
#     max_upload_size: int = 10 * 1024 * 1024  # 10MB
#     upload_dir: str = "./uploads"

#     # AI Model Configuration (add your API keys here)
#     openai_api_key: str | None = None
#     azure_openai_endpoint: str | None = None
#     azure_openai_key: str | None = None

#     class Config:
#         env_file = ".env"
#         case_sensitive = False


# settings = Settings()
