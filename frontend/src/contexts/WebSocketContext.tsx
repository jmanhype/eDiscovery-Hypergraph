import React, { createContext, useContext, useCallback, useState, useEffect } from 'react';
import { useWebSocket, MessageType, SubscriptionType } from '../hooks/useWebSocket';
import { useNotification } from '../components/ui';

interface WebSocketContextType {
  isConnected: boolean;
  subscribe: (type: SubscriptionType, resourceId?: string) => void;
  unsubscribe: (type: SubscriptionType, resourceId?: string) => void;
  workflowUpdates: Map<string, any>;
  documentUpdates: Map<string, any>;
  caseUpdates: Map<string, any>;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export function useWebSocketContext() {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within WebSocketProvider');
  }
  return context;
}

interface WebSocketProviderProps {
  children: React.ReactNode;
}

export function WebSocketProvider({ children }: WebSocketProviderProps) {
  const { showInfo, showSuccess, showError, NotificationComponent } = useNotification();
  const [workflowUpdates, setWorkflowUpdates] = useState(new Map<string, any>());
  const [documentUpdates, setDocumentUpdates] = useState(new Map<string, any>());
  const [caseUpdates, setCaseUpdates] = useState(new Map<string, any>());

  const handleMessage = useCallback((message: { type: MessageType; data?: any }) => {
    switch (message.type) {
      case MessageType.CONNECT:
        console.log('Connected to real-time updates');
        break;

      case MessageType.WORKFLOW_UPDATE:
        if (message.data?.resource_id) {
          setWorkflowUpdates(prev => {
            const updated = new Map(prev);
            updated.set(message.data.resource_id, message.data);
            return updated;
          });
          
          // Show notification for important status changes
          if (message.data.status === 'completed') {
            showSuccess(`Workflow completed: ${message.data.message}`);
          } else if (message.data.status === 'failed') {
            showError(`Workflow failed: ${message.data.error_message || message.data.message}`);
          } else if (message.data.current_step) {
            showInfo(`${message.data.message}`, `Step ${message.data.current_step}`);
          }
        }
        break;

      case MessageType.DOCUMENT_UPDATE:
        if (message.data?.resource_id) {
          setDocumentUpdates(prev => {
            const updated = new Map(prev);
            updated.set(message.data.resource_id, message.data);
            return updated;
          });
        }
        break;

      case MessageType.CASE_UPDATE:
        if (message.data?.resource_id) {
          setCaseUpdates(prev => {
            const updated = new Map(prev);
            updated.set(message.data.resource_id, message.data);
            return updated;
          });
        }
        break;

      case MessageType.NOTIFICATION:
        if (message.data?.type === 'error') {
          showError(message.data.message);
        } else if (message.data?.type === 'success') {
          showSuccess(message.data.message);
        } else {
          showInfo(message.data.message);
        }
        break;

      case MessageType.ERROR:
        console.error('WebSocket error:', message.data);
        showError(message.data?.message || 'Connection error');
        break;
    }
  }, [showInfo, showSuccess, showError]);

  const { isConnected, subscribe, unsubscribe } = useWebSocket({
    onMessage: handleMessage,
    onConnect: () => {
      console.log('WebSocket connected in context');
    },
    onDisconnect: () => {
      console.log('WebSocket disconnected in context');
    },
    onError: (error) => {
      console.error('WebSocket error in context:', error);
    },
  });

  // Clear old updates periodically
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      const maxAge = 5 * 60 * 1000; // 5 minutes

      // Clean up old workflow updates
      setWorkflowUpdates(prev => {
        const updated = new Map(prev);
        for (const [key, value] of updated) {
          const timestamp = new Date(value.timestamp).getTime();
          if (now - timestamp > maxAge) {
            updated.delete(key);
          }
        }
        return updated;
      });

      // Clean up old document updates
      setDocumentUpdates(prev => {
        const updated = new Map(prev);
        for (const [key, value] of updated) {
          const timestamp = new Date(value.timestamp).getTime();
          if (now - timestamp > maxAge) {
            updated.delete(key);
          }
        }
        return updated;
      });
    }, 60000); // Run every minute

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <WebSocketContext.Provider
        value={{
          isConnected,
          subscribe,
          unsubscribe,
          workflowUpdates,
          documentUpdates,
          caseUpdates,
        }}
      >
        {children}
      </WebSocketContext.Provider>
      <NotificationComponent />
    </>
  );
}