from fastapi import WebSocket, APIRouter, WebSocketDisconnect
from core.web_socket_manager import WebSocketManager
from pydantic import BaseModel

router = APIRouter()
web_socket_manager = WebSocketManager()


class MessageRequest(BaseModel):
    message: str


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await web_socket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive by waiting for messages
            data = await websocket.receive_text()
            # Optionally echo or broadcast received messages
            await web_socket_manager.send_message(f"Echo: {data}")
    except WebSocketDisconnect:
        web_socket_manager.disconnect(websocket)


@router.post("/")
async def send_message(request: MessageRequest):
    await web_socket_manager.send_message(request.message)
    return {"status": "sent", "message": request.message}