import { useEffect, useState, useCallback, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';

export enum MessageType {
  // Connection
  CONNECT = 'connect',
  DISCONNECT = 'disconnect',
  PING = 'ping',
  PONG = 'pong',
  
  // Subscriptions
  SUBSCRIBE = 'subscribe',
  UNSUBSCRIBE = 'unsubscribe',
  
  // Updates
  WORKFLOW_UPDATE = 'workflow_update',
  DOCUMENT_UPDATE = 'document_update',
  CASE_UPDATE = 'case_update',
  BATCH_UPDATE = 'batch_update',
  ENTITY_UPDATE = 'entity_update',
  
  // Notifications
  NOTIFICATION = 'notification',
  ERROR = 'error',
}

export enum SubscriptionType {
  WORKFLOW = 'workflow',
  DOCUMENT = 'document',
  CASE = 'case',
  BATCH = 'batch',
  ENTITY = 'entity',
  USER = 'user',
  ALL = 'all',
}

interface WebSocketMessage {
  type: MessageType;
  data?: any;
}

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Error) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    reconnectInterval = 5000,
    maxReconnectAttempts = 5,
  } = options;

  const { user, authToken } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const pingIntervalRef = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    if (!user || !authToken || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws/${user.id}?token=${authToken}`;
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setReconnectAttempts(0);
        onConnect?.();
        
        // Start ping interval
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: MessageType.PING }));
          }
        }, 30000); // Ping every 30 seconds
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage;
          onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError?.(new Error('WebSocket connection error'));
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        wsRef.current = null;
        onDisconnect?.();
        
        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }
        
        // Attempt to reconnect
        if (reconnectAttempts < maxReconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempts(prev => prev + 1);
            connect();
          }, reconnectInterval);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      onError?.(error as Error);
    }
  }, [user, authToken, onConnect, onDisconnect, onError, onMessage, reconnectAttempts, maxReconnectAttempts, reconnectInterval]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const send = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  const subscribe = useCallback((type: SubscriptionType, resourceId: string = '*') => {
    send({
      type: MessageType.SUBSCRIBE,
      data: {
        subscription_type: type,
        resource_id: resourceId,
      },
    });
  }, [send]);

  const unsubscribe = useCallback((type: SubscriptionType, resourceId: string = '*') => {
    send({
      type: MessageType.UNSUBSCRIBE,
      data: {
        subscription_type: type,
        resource_id: resourceId,
      },
    });
  }, [send]);

  // Connect when component mounts and user is authenticated
  useEffect(() => {
    if (user && authToken) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [user, authToken]); // Don't include connect/disconnect in deps to avoid loops

  return {
    isConnected,
    send,
    subscribe,
    unsubscribe,
    reconnect: connect,
    disconnect,
  };
}