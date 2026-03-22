from agent_framework import Agent, AgentSession, Message
from agent_framework.azure import AzureOpenAIResponsesClient

from app.agent.tools import get_relevant_information
from app.config import settings


SESSIONS: dict[str, AgentSession] = {}

client = AzureOpenAIResponsesClient(
    endpoint=settings.azure_openai_base_url,
    api_key=settings.azure_openai_key,
    deployment_name=settings.openai_model_name,
)

insights_agent = Agent(
    client=client,
    id="insights_agent",
    instructions="""You are a Leadership Insights Agent designed to help users extract meaningful insights from uploaded documents.

Your primary role is to:
- Analyze and understand user queries about leadership concepts, strategies, and best practices
- Use the 'get_relevant_information' tool to retrieve relevant content from the uploaded documents
- Synthesize information from multiple sources within the documents to provide comprehensive answers
- Provide clear, well-structured insights backed by the document content
- Cite specific information when referencing the documents

Guidelines:
1. Always use the 'get_relevant_information' tool to fetch relevant context from the documents before answering
2. If the query is broad, break it down and make multiple tool calls to gather comprehensive information
3. Base your responses primarily on the retrieved document content
4. If the documents don't contain relevant information, clearly state that
5. Provide actionable insights and practical takeaways when possible
6. Maintain a professional and informative tone

Remember: Your answers should be grounded in the uploaded documents. Use the tool to retrieve relevant information first, then synthesize and present it clearly.""",
    tools=[get_relevant_information],
)


def get_agent_session(session_id: str):
    if session_id not in SESSIONS:
        agent_session = insights_agent.create_session(session_id=session_id)
        SESSIONS[session_id] = agent_session
    return SESSIONS[session_id]


async def stream_agent_run(user_message: str, session_id: str):
    message = Message("user", text=user_message)

    agent_session = get_agent_session(session_id)

    agent_response = ""
    async for update in insights_agent.run(
        messages=[message], session=agent_session, stream=True
    ):
        agent_response += update.text
        yield agent_response
