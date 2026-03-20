import uvicorn
from agent_framework.observability import configure_otel_providers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.document import router as document_router


configure_otel_providers(enable_sensitive_data=True, vs_code_extension_port=4317)

app = FastAPI(
    title="Leadership Insights Agent API",
    description="API for Leadership Insights AI Agent",
    version="0.1.0",
)

app.include_router(document_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
