from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import List, Dict, Any

router = APIRouter()

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"[WS] Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return

        message_json = json.dumps(message, ensure_ascii=False)
        disconnected_clients = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                print(f"[WS] Error sending to client: {e}")
                disconnected_clients.append(connection)

        # Clean up disconnected clients
        for client in disconnected_clients:
            self.disconnect(client)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)

    try:
        while True:
            # Keep connection alive and handle any client messages
            data = await websocket.receive_text()

            # Echo back for testing
            await websocket.send_text(f"Echo: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"[WS] Error: {e}")
        manager.disconnect(websocket)

@router.websocket("/ws/alerts")
async def alerts_websocket(websocket: WebSocket):
    """WebSocket specifically for alert updates"""
    await manager.connect(websocket)

    try:
        while True:
            # Send periodic updates (every 30 seconds)
            await asyncio.sleep(30)

            # Send current stats
            try:
                # This would normally fetch from database
                # For now, send a heartbeat
                await websocket.send_text(json.dumps({
                    "type": "heartbeat",
                    "message": "Connection alive",
                    "timestamp": asyncio.get_event_loop().time()
                }, ensure_ascii=False))
            except Exception as e:
                print(f"[WS] Error sending heartbeat: {e}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"[WS] Error: {e}")
        manager.disconnect(websocket)

# Function to broadcast alerts to all connected clients
async def broadcast_alert(alert_data: Dict[str, Any]):
    """Broadcast new alert to all connected clients"""
    message = {
        "type": "new_alert",
        "data": alert_data,
        "timestamp": asyncio.get_event_loop().time()
    }

    await manager.broadcast(message)

async def broadcast_stats(stats_data: Dict[str, Any]):
    """Broadcast updated stats to all connected clients"""
    message = {
        "type": "stats_update",
        "data": stats_data,
        "timestamp": asyncio.get_event_loop().time()
    }

    await manager.broadcast(message)

# Get connection count
def get_connection_count():
    """Get number of active WebSocket connections"""
    return len(manager.active_connections)
