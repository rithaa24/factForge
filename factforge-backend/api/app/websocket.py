"""
WebSocket service for real-time events
"""
import json
import logging
from typing import Dict, Any, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
import asyncio
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        # Store active connections
        self.active_connections: List[WebSocket] = []
        # Store connections by user ID
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        # Store connections by role
        self.role_connections: Dict[str, Set[WebSocket]] = {
            "admin": set(),
            "reviewer": set(),
            "user": set()
        }
    
    async def connect(self, websocket: WebSocket, user_id: str = None, role: str = "user"):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)
        
        if role in self.role_connections:
            self.role_connections[role].add(websocket)
        
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_id: str = None, role: str = "user"):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        if role in self.role_connections:
            self.role_connections[role].discard(websocket)
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to a specific WebSocket"""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
    
    async def send_to_user(self, message: str, user_id: str):
        """Send message to all connections of a specific user"""
        if user_id in self.user_connections:
            for websocket in self.user_connections[user_id].copy():
                await self.send_personal_message(message, websocket)
    
    async def send_to_role(self, message: str, role: str):
        """Send message to all connections with a specific role"""
        if role in self.role_connections:
            for websocket in self.role_connections[role].copy():
                await self.send_personal_message(message, websocket)
    
    async def broadcast(self, message: str):
        """Broadcast message to all active connections"""
        for websocket in self.active_connections.copy():
            await self.send_personal_message(message, websocket)
    
    async def send_event(self, event_type: str, data: Dict[str, Any], 
                        target_user: str = None, target_role: str = None):
        """Send a structured event"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        message = json.dumps(event)
        
        if target_user:
            await self.send_to_user(message, target_user)
        elif target_role:
            await self.send_to_role(message, target_role)
        else:
            await self.broadcast(message)

# Global connection manager
manager = ConnectionManager()

class WebSocketService:
    """Service for handling WebSocket events"""
    
    def __init__(self):
        self.manager = manager
    
    async def handle_connection(self, websocket: WebSocket, user_id: str = None, role: str = "user"):
        """Handle a WebSocket connection"""
        await self.manager.connect(websocket, user_id, role)
        
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                
                try:
                    message = json.loads(data)
                    await self.handle_message(websocket, message)
                except json.JSONDecodeError:
                    await self.send_error(websocket, "Invalid JSON format")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    await self.send_error(websocket, "Internal server error")
        
        except WebSocketDisconnect:
            self.manager.disconnect(websocket, user_id, role)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            self.manager.disconnect(websocket, user_id, role)
    
    async def handle_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        message_type = message.get("type")
        
        if message_type == "ping":
            await self.send_pong(websocket)
        elif message_type == "subscribe":
            # Handle subscription to specific event types
            event_types = message.get("event_types", [])
            await self.handle_subscription(websocket, event_types)
        else:
            await self.send_error(websocket, f"Unknown message type: {message_type}")
    
    async def send_pong(self, websocket: WebSocket):
        """Send pong response"""
        response = {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
        await self.manager.send_personal_message(json.dumps(response), websocket)
    
    async def handle_subscription(self, websocket: WebSocket, event_types: List[str]):
        """Handle event subscription"""
        # For now, just acknowledge the subscription
        response = {
            "type": "subscription_confirmed",
            "event_types": event_types,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.send_personal_message(json.dumps(response), websocket)
    
    async def send_error(self, websocket: WebSocket, error_message: str):
        """Send error message"""
        error = {
            "type": "error",
            "message": error_message,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.send_personal_message(json.dumps(error), websocket)
    
    # Event broadcasting methods
    async def broadcast_crawler_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast crawler-related event"""
        await self.manager.send_event(f"crawler:{event_type}", data)
    
    async def broadcast_ingest_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast ingestion-related event"""
        await self.manager.send_event(f"ingest:{event_type}", data)
    
    async def broadcast_review_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast review-related event"""
        await self.manager.send_event(f"review:{event_type}", data, target_role="reviewer")
    
    async def broadcast_check_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast fact-check related event"""
        await self.manager.send_event(f"check:{event_type}", data)
    
    async def broadcast_admin_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast admin-related event"""
        await self.manager.send_event(f"admin:{event_type}", data, target_role="admin")

# Global WebSocket service
websocket_service = WebSocketService()

# Convenience functions for broadcasting events
async def broadcast_crawler_found(url: str, language: str, heuristic_score: float):
    """Broadcast when crawler finds new content"""
    await websocket_service.broadcast_crawler_event("found", {
        "url": url,
        "language": language,
        "heuristic_score": heuristic_score
    })

async def broadcast_ingest_completed(doc_id: str, label: str, score: float):
    """Broadcast when ingestion is completed"""
    await websocket_service.broadcast_ingest_event("completed", {
        "doc_id": doc_id,
        "label": label,
        "score": score
    })

async def broadcast_review_queued(doc_id: str, language: str, score: float):
    """Broadcast when item is queued for review"""
    await websocket_service.broadcast_review_event("queued", {
        "doc_id": doc_id,
        "language": language,
        "score": score
    })

async def broadcast_review_approved(doc_id: str, reviewer_id: str):
    """Broadcast when review is approved"""
    await websocket_service.broadcast_review_event("approved", {
        "doc_id": doc_id,
        "reviewer_id": reviewer_id
    })

async def broadcast_check_completed(request_id: str, verdict: str, latency_ms: int):
    """Broadcast when fact-check is completed"""
    await websocket_service.broadcast_check_event("completed", {
        "request_id": request_id,
        "verdict": verdict,
        "latency_ms": latency_ms
    })

async def broadcast_admin_alert(alert_type: str, message: str):
    """Broadcast admin alert"""
    await websocket_service.broadcast_admin_event("alert", {
        "alert_type": alert_type,
        "message": message
    })
