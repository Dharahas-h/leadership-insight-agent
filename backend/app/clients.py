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
        print("#" * 80)
        print("#" * 80)
        print("Agent client initialized successfully")
        print("Testing connection parameters")
        # Test connection with a simple request
        await agent_client.client.responses.create(
            input="test",
            max_output_tokens=20,
            instructions="You are a friendly agent",
            model=settings.model_name,
        )
        print("Agent client connection verified")

        print("#" * 80)
        print("#" * 80)
        # Validate embedding client
        embedding_client = get_embedding_client()
        print("Embedding client initialized successfully")
        print("Testing connection parameters")
        # Test connection with a simple embedding request
        await embedding_client.client.embeddings.create(
            input="test", model=settings.embedding_model_name
        )
        print("Embedding client connection verified")

        print("All connections validated successfully\n")
        print("#" * 80)
        print("#" * 80)

    except Exception as e:
        print(
            "Connection validation failed: Update the connection varaibles properly..."
        )
        raise e


def get_agent_client():
    try:
        if settings.open_ai_key:
            return OpenAIResponsesClient(
                base_url=settings.open_ai_url if settings.open_ai_url else None,
                api_key=settings.open_ai_key,
                model_id=settings.model_name,
            )
        if settings.openai_azure_key and settings.openai_azure_base_url:
            return AzureOpenAIResponsesClient(
                endpoint=settings.openai_azure_base_url,
                api_key=settings.openai_azure_key,
                deployment_name=settings.model_name,
                api_version=settings.openai_azure_api_version
                if settings.openai_azure_api_version
                else None,
            )
        raise ValueError(
            "OpenAI or Azure OpenAI configuration not set. "
            "Please set either OPENAI_KEY or both AZURE_OPENAI_KEY and AZURE_OPENAI_BASE_URL environment variables."
        )
    except ValueError as e:
        raise e


def get_embedding_client():
    try:
        if settings.open_ai_key:
            return OpenAIEmbeddingClient(
                base_url=settings.open_ai_url if settings.open_ai_url else None,
                api_key=settings.open_ai_key,
                model_id=settings.embedding_model_name,
            )

        if settings.openai_azure_key and settings.openai_azure_base_url:
            return AzureOpenAIEmbeddingClient(
                api_key=settings.openai_azure_key,
                endpoint=settings.openai_azure_base_url,
                deployment_name=settings.embedding_model_name,
            )

        raise ValueError(
            "OpenAI or Azure OpenAI embedding configuration not set. "
            "Please set either OPENAI_KEY or both AZURE_OPENAI_KEY and AZURE_OPENAI_BASE_URL environment variables."
        )
    except ValueError as e:
        raise e
