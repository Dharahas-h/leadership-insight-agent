from agent_framework.azure import AzureOpenAIEmbeddingClient, AzureOpenAIResponsesClient
from agent_framework.openai import OpenAIEmbeddingClient, OpenAIResponsesClient

from app.config import settings


async def validate_connections():
    """Validate OpenAI and embedding client connections before startup.

    Raises:
        ValueError: If configuration is invalid
        Exception: If connection test fails
    """
    print("Validating connections...")

    try:
        # Validate agent client
        agent_client = get_agent_client()
        print("Agent client initialized successfully")

        # Test connection with a simple request
        await agent_client.client.responses.create(
            input="test",
            max_output_tokens=1,
            instructions="You are a friendly agent",
        )
        print("Agent client connection verified")

        # Validate embedding client
        embedding_client = get_embedding_client()
        print("Embedding client initialized successfully")

        # Test connection with a simple embedding request
        await embedding_client.client.embeddings.create(input="test")
        print("Embedding client connection verified")

        print("All connections validated successfully\n")

    except Exception as e:
        print(
            "Connection validation failed: Update the connection varaibles properly..."
        )
        raise e


def get_agent_client():
    try:
        if settings.openai_key:
            return OpenAIResponsesClient(
                model_id=settings.openai_model_name,
                api_key=settings.openai_key,
                base_url=settings.openai_base_url if settings.openai_base_url else None,
            )
        if settings.azure_openai_key and settings.azure_openai_base_url:
            return AzureOpenAIResponsesClient(
                endpoint=settings.azure_openai_base_url,
                api_key=settings.azure_openai_key,
                deployment_name=settings.openai_model_name,
            )
        raise ValueError(
            "OpenAI or Azure OpenAI configuration not set. "
            "Please set either OPENAI_KEY or both AZURE_OPENAI_KEY and AZURE_OPENAI_BASE_URL environment variables."
        )
    except ValueError as e:
        raise e


def get_embedding_client():
    try:
        if settings.openai_key:
            return OpenAIEmbeddingClient(
                model_id=settings.embedding_model_name, api_key=settings.openai_key
            )
        if settings.azure_openai_key and settings.azure_openai_base_url:
            return AzureOpenAIEmbeddingClient(
                api_key=settings.azure_openai_key,
                endpoint=settings.azure_openai_base_url,
                deployment_name=settings.embedding_model_name,
            )
        raise ValueError(
            "OpenAI or Azure OpenAI embedding configuration not set. "
            "Please set either OPENAI_KEY or both AZURE_OPENAI_KEY and AZURE_OPENAI_BASE_URL environment variables."
        )
    except ValueError as e:
        raise e
