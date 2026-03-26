import asyncio
import sys

import uvicorn
from agent_framework.observability import configure_otel_providers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.clients import validate_connections
from app.config import settings
from app.routers.chat import router as chat_router
from app.routers.document import router as document_router


app = FastAPI(
    title="Leadership Insights Agent API",
    description="API for Leadership Insights AI Agent",
    version="0.1.0",
)

app.include_router(document_router)
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    if settings.vscode_extension_port != 0:
        configure_otel_providers(
            enable_sensitive_data=True,
            vs_code_extension_port=settings.vscode_extension_port,
            enable_console_exporters=True,
        )
    try:
        asyncio.run(validate_connections())
    except Exception as e:
        print("Exception: ", e)
        sys.exit()

    uvicorn.run("main:app", host=settings.api_host, port=settings.api_port)
