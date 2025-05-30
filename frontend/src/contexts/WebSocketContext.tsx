import React, { createContext, useContext, useCallback, useState, useEffect } from 'react';
import { useWebSocket, MessageType, SubscriptionType } from '../hooks/useWebSocket';
import { useNotification } from '../components/ui';

interface WorkflowUpdate {
  resource_id?: string;
  status?: string;
  message?: string;
  error_message?: string;
  current_step?: number;
}

interface ResourceUpdate {
  resource_id?: string;
  [key: string]: unknown;
}

interface NotificationData {
  type?: string;
  message?: string;
}

interface WebSocketContextType {
  isConnected: boolean;
  subscribe: (type: SubscriptionType, resourceId?: string) => void;
  unsubscribe: (type: SubscriptionType, resourceId?: string) => void;
  workflowUpdates: Map<string, unknown>;
  documentUpdates: Map<string, unknown>;
  caseUpdates: Map<string, unknown>;
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
  const [workflowUpdates, setWorkflowUpdates] = useState(new Map<string, unknown>());
  const [documentUpdates, setDocumentUpdates] = useState(new Map<string, unknown>());
  const [caseUpdates, setCaseUpdates] = useState(new Map<string, unknown>());

  const handleMessage = useCallback((message: { type: MessageType; data?: unknown }) => {
    switch (message.type) {
      case MessageType.CONNECT:
        console.log('Connected to real-time updates');
        break;

      case MessageType.WORKFLOW_UPDATE:
        {
          const workflowData = message.data as WorkflowUpdate;
          if (workflowData?.resource_id) {
            setWorkflowUpdates(prev => {
              const updated = new Map(prev);
              updated.set(workflowData.resource_id!, workflowData);
              return updated;
            });
            
            // Show notification for important status changes
            if (workflowData.status === 'completed') {
              showSuccess(`Workflow completed: ${workflowData.message || ''}`);
            } else if (workflowData.status === 'failed') {
              showError(`Workflow failed: ${workflowData.error_message || workflowData.message || ''}`);
            } else if (workflowData.current_step) {
              showInfo(`${workflowData.message || ''}`, `Step ${workflowData.current_step}`);
            }
          }
        }
        break;

      case MessageType.DOCUMENT_UPDATE:
        {
          const documentData = message.data as ResourceUpdate;
          if (documentData?.resource_id) {
            setDocumentUpdates(prev => {
              const updated = new Map(prev);
              updated.set(documentData.resource_id!, documentData);
              return updated;
            });
          }
        }
        break;

      case MessageType.CASE_UPDATE:
        {
          const caseData = message.data as ResourceUpdate;
          if (caseData?.resource_id) {
            setCaseUpdates(prev => {
              const updated = new Map(prev);
              updated.set(caseData.resource_id!, caseData);
              return updated;
            });
          }
        }
        break;

      case MessageType.NOTIFICATION:
        {
          const notificationData = message.data as NotificationData;
          if (notificationData?.type === 'error') {
            showError(notificationData.message || 'Error occurred');
          } else if (notificationData?.type === 'success') {
            showSuccess(notificationData.message || 'Success');
          } else {
            showInfo(notificationData.message || 'Notification');
          }
        }
        break;

      case MessageType.ERROR:
        {
          console.error('WebSocket error:', message.data);
          const errorData = message.data as { message?: string };
          showError(errorData?.message || 'Connection error');
        }
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
          const updateValue = value as { timestamp?: string };
          if (!updateValue.timestamp) continue;
          const timestamp = new Date(updateValue.timestamp).getTime();
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
          const updateValue = value as { timestamp?: string };
          if (!updateValue.timestamp) continue;
          const timestamp = new Date(updateValue.timestamp).getTime();
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