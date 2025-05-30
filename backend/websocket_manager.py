"""
WebSocket connection manager for real-time updates
"""
from typing import Dict, Set, List, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
import json
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class MessageType(str, Enum):
    """Types of WebSocket messages"""
    # Connection
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"
    
    # Subscriptions
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    
    # Updates
    WORKFLOW_UPDATE = "workflow_update"
    DOCUMENT_UPDATE = "document_update"
    CASE_UPDATE = "case_update"
    BATCH_UPDATE = "batch_update"
    ENTITY_UPDATE = "entity_update"
    
    # Notifications
    NOTIFICATION = "notification"
    ERROR = "error"

class SubscriptionType(str, Enum):
    """Types of subscriptions available"""
    WORKFLOW = "workflow"
    DOCUMENT = "document"
    CASE = "case"
    BATCH = "batch"
    ENTITY = "entity"
    USER = "user"  # User-specific notifications
    ALL = "all"    # All updates (admin only)

class ConnectionManager:
    """Manages WebSocket connections and message routing"""
    
    def __init__(self):
        # Active connections by user ID
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
        # Subscriptions: subscription_type -> resource_id -> set of user_ids
        self.subscriptions: Dict[str, Dict[str, Set[str]]] = {
            sub_type.value: {} for sub_type in SubscriptionType
        }
        
        # User roles for authorization
        self.user_roles: Dict[str, str] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, user_role: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Add to active connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # Store user role
        self.user_roles[user_id] = user_role
        
        # Send connection confirmation
        await self._send_message(websocket, {
            "type": MessageType.CONNECT,
            "data": {
                "user_id": user_id,
                "connected_at": datetime.utcnow().isoformat(),
                "message": "Connected to eDiscovery real-time updates"
            }
        })
        
        logger.info(f"User {user_id} connected via WebSocket")
    
    async def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            # Remove empty sets
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                
                # Clean up subscriptions
                for sub_type in self.subscriptions.values():
                    for resource_id in sub_type.values():
                        resource_id.discard(user_id)
        
        logger.info(f"User {user_id} disconnected from WebSocket")
    
    async def subscribe(self, user_id: str, subscription_type: str, resource_id: str = "*"):
        """Subscribe a user to updates for a specific resource"""
        if subscription_type not in self.subscriptions:
            raise ValueError(f"Invalid subscription type: {subscription_type}")
        
        # Check authorization
        if subscription_type == SubscriptionType.ALL and self.user_roles.get(user_id) != "admin":
            raise PermissionError("Only admins can subscribe to all updates")
        
        # Add subscription
        if resource_id not in self.subscriptions[subscription_type]:
            self.subscriptions[subscription_type][resource_id] = set()
        self.subscriptions[subscription_type][resource_id].add(user_id)
        
        # Send confirmation
        await self._send_to_user(user_id, {
            "type": MessageType.SUBSCRIBE,
            "data": {
                "subscription_type": subscription_type,
                "resource_id": resource_id,
                "subscribed_at": datetime.utcnow().isoformat()
            }
        })
        
        logger.info(f"User {user_id} subscribed to {subscription_type}:{resource_id}")
    
    async def unsubscribe(self, user_id: str, subscription_type: str, resource_id: str = "*"):
        """Unsubscribe a user from updates"""
        if subscription_type in self.subscriptions:
            if resource_id in self.subscriptions[subscription_type]:
                self.subscriptions[subscription_type][resource_id].discard(user_id)
                
                # Clean up empty sets
                if not self.subscriptions[subscription_type][resource_id]:
                    del self.subscriptions[subscription_type][resource_id]
        
        # Send confirmation
        await self._send_to_user(user_id, {
            "type": MessageType.UNSUBSCRIBE,
            "data": {
                "subscription_type": subscription_type,
                "resource_id": resource_id,
                "unsubscribed_at": datetime.utcnow().isoformat()
            }
        })
        
        logger.info(f"User {user_id} unsubscribed from {subscription_type}:{resource_id}")
    
    async def send_workflow_update(self, workflow_id: str, update_data: Dict[str, Any]):
        """Send workflow update to subscribed users"""
        await self._broadcast_update(
            SubscriptionType.WORKFLOW,
            workflow_id,
            MessageType.WORKFLOW_UPDATE,
            update_data
        )
    
    async def send_document_update(self, document_id: str, update_data: Dict[str, Any]):
        """Send document update to subscribed users"""
        await self._broadcast_update(
            SubscriptionType.DOCUMENT,
            document_id,
            MessageType.DOCUMENT_UPDATE,
            update_data
        )
    
    async def send_case_update(self, case_id: str, update_data: Dict[str, Any]):
        """Send case update to subscribed users"""
        await self._broadcast_update(
            SubscriptionType.CASE,
            case_id,
            MessageType.CASE_UPDATE,
            update_data
        )
    
    async def send_batch_update(self, batch_id: str, update_data: Dict[str, Any]):
        """Send batch update to subscribed users"""
        await self._broadcast_update(
            SubscriptionType.BATCH,
            batch_id,
            MessageType.BATCH_UPDATE,
            update_data
        )
    
    async def send_notification(self, user_id: str, notification: Dict[str, Any]):
        """Send a notification to a specific user"""
        await self._send_to_user(user_id, {
            "type": MessageType.NOTIFICATION,
            "data": notification
        })
    
    async def broadcast_to_role(self, role: str, message: Dict[str, Any]):
        """Broadcast a message to all users with a specific role"""
        for user_id, user_role in self.user_roles.items():
            if user_role == role:
                await self._send_to_user(user_id, message)
    
    async def handle_message(self, websocket: WebSocket, user_id: str, message: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        msg_type = message.get("type")
        data = message.get("data", {})
        
        try:
            if msg_type == MessageType.PING:
                await self._send_message(websocket, {"type": MessageType.PONG})
            
            elif msg_type == MessageType.SUBSCRIBE:
                await self.subscribe(
                    user_id,
                    data.get("subscription_type"),
                    data.get("resource_id", "*")
                )
            
            elif msg_type == MessageType.UNSUBSCRIBE:
                await self.unsubscribe(
                    user_id,
                    data.get("subscription_type"),
                    data.get("resource_id", "*")
                )
            
            else:
                await self._send_message(websocket, {
                    "type": MessageType.ERROR,
                    "data": {"message": f"Unknown message type: {msg_type}"}
                })
        
        except Exception as e:
            logger.error(f"Error handling message from {user_id}: {str(e)}")
            await self._send_message(websocket, {
                "type": MessageType.ERROR,
                "data": {"message": str(e)}
            })
    
    async def _broadcast_update(
        self,
        subscription_type: SubscriptionType,
        resource_id: str,
        message_type: MessageType,
        data: Dict[str, Any]
    ):
        """Broadcast an update to all subscribed users"""
        # Get users subscribed to this specific resource
        specific_users = self.subscriptions[subscription_type.value].get(resource_id, set())
        
        # Get users subscribed to all resources of this type
        wildcard_users = self.subscriptions[subscription_type.value].get("*", set())
        
        # Get users subscribed to all updates
        all_users = self.subscriptions[SubscriptionType.ALL.value].get("*", set())
        
        # Combine all subscribed users
        target_users = specific_users | wildcard_users | all_users
        
        # Send update to all target users
        message = {
            "type": message_type,
            "data": {
                "resource_id": resource_id,
                "timestamp": datetime.utcnow().isoformat(),
                **data
            }
        }
        
        for user_id in target_users:
            await self._send_to_user(user_id, message)
    
    async def _send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send a message to all connections for a user"""
        if user_id in self.active_connections:
            dead_connections = set()
            
            for websocket in self.active_connections[user_id]:
                try:
                    await self._send_message(websocket, message)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {str(e)}")
                    dead_connections.add(websocket)
            
            # Clean up dead connections
            for websocket in dead_connections:
                self.active_connections[user_id].discard(websocket)
    
    async def _send_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send a message through a WebSocket connection"""
        await websocket.send_json(message)

# Global connection manager instance
manager = ConnectionManager()