import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.agent.insights_agent import stream_agent_run


router = APIRouter(tags=["Agent Chat"])


@router.websocket("/chat")
async def chat(socket: WebSocket):
    await socket.accept()
    session_id = socket.query_params.get("sessionId", "")
    try:
        if session_id == "":
            raise Exception("Session ID not present")
        while True:
            payload = await socket.receive_json()
            await socket.send_json({"type": "start", "message": ""})
            async for message in stream_agent_run(payload["message"], session_id):
                await socket.send_json({"type": "message", "message": message})
    except WebSocketDisconnect:
        print("/chat websocket connection closed")
    except Exception as e:
        await socket.send_text(json.dumps({"type": "error", "content": e}))
        await socket.close()
        print("Exception: ", e.with_traceback())
