from agent_framework.azure import AzureOpenAIEmbeddingClient

from app.config import settings


embedding_client = AzureOpenAIEmbeddingClient(
    api_key=settings.azure_openai_key,
    endpoint=settings.azure_openai_base_url,
    deployment_name=settings.embedding_model_name,
)
