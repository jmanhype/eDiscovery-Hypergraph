---
id: websocket-api
title: WebSocket API
sidebar_label: WebSocket API
---

# WebSocket API

The eDiscovery Hypergraph platform provides WebSocket connections for real-time bidirectional communication, enabling live updates, collaborative features, and streaming data.

## Connection

### WebSocket Endpoint

```
wss://api.ediscovery-hypergraph.com/socket
```

For local development:
```
ws://localhost:4000/socket
```

### Connection Example

```javascript
// JavaScript/TypeScript
import { Socket } from 'phoenix';

const socket = new Socket('wss://api.ediscovery-hypergraph.com/socket', {
  params: { 
    token: 'YOUR_AUTH_TOKEN',
    client_version: '1.0.0'
  },
  reconnectAfterMs: (tries) => [1000, 2000, 5000, 10000][tries - 1] || 10000,
  heartbeatIntervalMs: 30000
});

socket.onOpen(() => console.log('Connected'));
socket.onError((e) => console.error('Connection error:', e));
socket.onClose(() => console.log('Disconnected'));

socket.connect();
```

### Authentication

Include your authentication token in the connection params:

```python
# Python example using websocket-client
import websocket
import json

def on_open(ws):
    # Authenticate after connection
    ws.send(json.dumps({
        "topic": "auth",
        "event": "authenticate",
        "payload": {
            "token": "YOUR_AUTH_TOKEN"
        },
        "ref": "1"
    }))

ws = websocket.WebSocketApp(
    "wss://api.ediscovery-hypergraph.com/socket/websocket",
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()
```

## Channels

### Case Channel

Monitor all activity for a specific case:

```javascript
// Join case channel
const caseChannel = socket.channel(`case:${caseId}`, {
  user_id: userId
});

// Listen for events
caseChannel.on('document:uploaded', (payload) => {
  console.log('New document:', payload);
  updateDocumentList(payload.document);
});

caseChannel.on('document:processed', (payload) => {
  console.log('Document processed:', payload);
  updateProcessingStatus(payload.document_id, payload.status);
});

caseChannel.on('user:joined', (payload) => {
  console.log('User joined:', payload.user);
  showNotification(`${payload.user.name} joined the case`);
});

caseChannel.on('workflow:completed', (payload) => {
  console.log('Workflow completed:', payload);
  refreshWorkflowStatus(payload.workflow_id);
});

// Join with error handling
caseChannel.join()
  .receive('ok', (resp) => console.log('Joined case channel', resp))
  .receive('error', (resp) => console.error('Unable to join', resp))
  .receive('timeout', () => console.error('Connection timeout'));
```

### Document Channel

Real-time collaboration on documents:

```javascript
const docChannel = socket.channel(`document:${documentId}`, {
  capabilities: ['read', 'annotate']
});

// Document events
docChannel.on('annotation:added', (payload) => {
  renderAnnotation(payload.annotation);
});

docChannel.on('annotation:removed', (payload) => {
  removeAnnotation(payload.annotation_id);
});

docChannel.on('user:viewing', (payload) => {
  showViewingIndicator(payload.user);
});

docChannel.on('privilege:updated', (payload) => {
  updatePrivilegeStatus(payload.privilege);
});

// Send annotation
docChannel.push('add_annotation', {
  text: 'Important clause',
  position: { page: 1, x: 100, y: 200 },
  type: 'highlight'
})
  .receive('ok', (resp) => console.log('Annotation added', resp))
  .receive('error', (resp) => console.error('Failed to add annotation', resp));
```

### Processing Channel

Monitor document processing in real-time:

```javascript
const processingChannel = socket.channel(`processing:${jobId}`);

processingChannel.on('progress', (payload) => {
  updateProgressBar(payload.percentage);
  updateStatus(payload.current_operation);
});

processingChannel.on('document:completed', (payload) => {
  markDocumentComplete(payload.document_id);
  displayResults(payload.results);
});

processingChannel.on('error', (payload) => {
  showError(payload.error);
  handleProcessingError(payload.document_id, payload.error);
});

processingChannel.on('job:completed', (payload) => {
  showCompletionNotification(payload.summary);
  redirectToResults(payload.job_id);
});
```

### Search Channel

Live search with streaming results:

```javascript
const searchChannel = socket.channel('search:live');

// Streaming search
searchChannel.push('search', {
  query: 'breach of contract',
  filters: {
    case_ids: ['case_123'],
    date_range: { start: '2023-01-01', end: '2023-12-31' }
  },
  stream: true
})
  .receive('ok', (resp) => {
    console.log('Search started:', resp.search_id);
  });

// Receive streaming results
searchChannel.on('result', (payload) => {
  addSearchResult(payload.document);
  updateResultCount(payload.total_so_far);
});

searchChannel.on('search:complete', (payload) => {
  finalizeSearch(payload.total_results, payload.search_time);
});

// Cancel search
searchChannel.push('cancel_search', { search_id: searchId });
```

## Message Protocol

### Message Format

All WebSocket messages follow this structure:

```json
{
  "topic": "case:123",
  "event": "document:processed",
  "payload": {
    "document_id": "doc_456",
    "status": "completed",
    "results": {
      "entities": [...],
      "summary": "..."
    }
  },
  "ref": "unique_ref_123",
  "join_ref": "join_ref_456"
}
```

### Event Types

#### System Events

| Event | Description | Payload |
|-------|-------------|---------|
| `phx_join` | Channel join request | Join parameters |
| `phx_leave` | Channel leave | Empty |
| `phx_reply` | Server response | Response data |
| `phx_error` | Error occurred | Error details |
| `phx_close` | Channel closed | Close reason |
| `heartbeat` | Keep-alive ping | Empty |

#### Application Events

| Event | Channel | Description |
|-------|---------|-------------|
| `document:uploaded` | `case:*` | New document uploaded |
| `document:processed` | `case:*` | Document processing complete |
| `workflow:started` | `case:*` | Workflow execution started |
| `workflow:completed` | `case:*` | Workflow execution finished |
| `annotation:added` | `document:*` | Annotation added to document |
| `privilege:updated` | `document:*` | Privilege status changed |
| `user:joined` | `case:*` | User joined the case |
| `user:left` | `case:*` | User left the case |
| `search:result` | `search:*` | Search result found |
| `processing:progress` | `processing:*` | Processing progress update |

## Presence

Track who's online and their activity:

```javascript
import { Presence } from 'phoenix';

const presence = new Presence(caseChannel);

// Track presence state
presence.onSync(() => {
  const users = [];
  
  presence.list((id, { metas: [first, ...rest] }) => {
    users.push({
      id: id,
      name: first.name,
      status: first.status,
      activity: first.activity
    });
  });
  
  updateOnlineUsers(users);
});

// User joined
presence.onJoin((id, current, newPres) => {
  if (!current) {
    console.log(`${newPres.metas[0].name} has joined`);
  }
});

// User left
presence.onLeave((id, current, leftPres) => {
  if (current.metas.length === 0) {
    console.log(`${leftPres.metas[0].name} has left`);
  }
});

// Update your status
caseChannel.push('presence:update', {
  status: 'reviewing',
  activity: 'Reviewing privileged documents',
  location: 'document_list'
});
```

## Collaborative Features

### Real-time Cursor Tracking

```javascript
const collaborationChannel = socket.channel(`collaboration:${documentId}`);

// Share cursor position
document.addEventListener('mousemove', throttle((e) => {
  collaborationChannel.push('cursor:move', {
    x: e.pageX,
    y: e.pageY,
    page: currentPage
  });
}, 50));

// Display other users' cursors
collaborationChannel.on('cursor:position', (payload) => {
  updateUserCursor(payload.user_id, payload.x, payload.y);
});

// Selection sharing
document.addEventListener('mouseup', () => {
  const selection = window.getSelection();
  if (selection.toString()) {
    collaborationChannel.push('selection:share', {
      text: selection.toString(),
      range: getSelectionRange()
    });
  }
});
```

### Live Collaborative Editing

```javascript
// Operational Transform for conflict resolution
import { TextOperation } from 'ot';

const otChannel = socket.channel(`ot:${documentId}`);

let clientRevision = 0;
let serverRevision = 0;
let inflightOperation = null;
let buffer = null;

// Send operation
function sendOperation(operation) {
  if (inflightOperation) {
    buffer = buffer ? buffer.compose(operation) : operation;
  } else {
    inflightOperation = operation;
    otChannel.push('operation', {
      operation: operation.toJSON(),
      revision: serverRevision
    });
  }
}

// Receive operation
otChannel.on('operation', (payload) => {
  const operation = TextOperation.fromJSON(payload.operation);
  
  if (inflightOperation) {
    const pair = TextOperation.transform(inflightOperation, operation);
    inflightOperation = pair[0];
    operation = pair[1];
  }
  
  if (buffer) {
    const pair = TextOperation.transform(buffer, operation);
    buffer = pair[0];
  }
  
  applyOperation(operation);
  serverRevision = payload.revision;
});

// Acknowledgment
otChannel.on('ack', (payload) => {
  serverRevision = payload.revision;
  inflightOperation = null;
  
  if (buffer) {
    sendOperation(buffer);
    buffer = null;
  }
});
```

## Error Handling

### Connection Error Handling

```javascript
class RobustWebSocket {
  constructor(url, options) {
    this.url = url;
    this.options = options;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 1000;
    this.socket = null;
  }
  
  connect() {
    this.socket = new Socket(this.url, this.options);
    
    this.socket.onError((error) => {
      console.error('WebSocket error:', error);
      this.handleError(error);
    });
    
    this.socket.onClose((event) => {
      console.log('WebSocket closed:', event);
      if (!event.wasClean) {
        this.reconnect();
      }
    });
    
    this.socket.connect();
  }
  
  reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.onMaxReconnectAttemptsReached();
      return;
    }
    
    this.reconnectAttempts++;
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      30000
    );
    
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      this.connect();
    }, delay);
  }
  
  handleError(error) {
    // Log to error tracking service
    errorTracker.log('websocket_error', {
      error: error.message,
      reconnectAttempts: this.reconnectAttempts,
      timestamp: new Date().toISOString()
    });
  }
}
```

### Channel Error Recovery

```javascript
function joinChannelWithRetry(channel, maxAttempts = 5) {
  let attempts = 0;
  
  function attemptJoin() {
    attempts++;
    
    channel.join()
      .receive('ok', (resp) => {
        console.log('Successfully joined channel', resp);
        attempts = 0; // Reset on success
      })
      .receive('error', (resp) => {
        console.error(`Failed to join channel (attempt ${attempts}):`, resp);
        
        if (attempts < maxAttempts) {
          const delay = Math.min(1000 * Math.pow(2, attempts - 1), 10000);
          setTimeout(attemptJoin, delay);
        } else {
          handleChannelJoinFailure(channel, resp);
        }
      })
      .receive('timeout', () => {
        console.error('Channel join timeout');
        if (attempts < maxAttempts) {
          attemptJoin();
        }
      });
  }
  
  attemptJoin();
}
```

## Performance Optimization

### Message Batching

```javascript
class BatchedChannel {
  constructor(channel, batchInterval = 100) {
    this.channel = channel;
    this.batchInterval = batchInterval;
    this.messageQueue = [];
    this.batchTimer = null;
  }
  
  push(event, payload) {
    this.messageQueue.push({ event, payload });
    
    if (!this.batchTimer) {
      this.batchTimer = setTimeout(() => {
        this.flush();
      }, this.batchInterval);
    }
  }
  
  flush() {
    if (this.messageQueue.length === 0) return;
    
    const batch = this.messageQueue.splice(0);
    this.channel.push('batch', { messages: batch })
      .receive('ok', () => console.log(`Sent ${batch.length} messages`))
      .receive('error', (err) => {
        console.error('Batch send failed:', err);
        // Re-queue messages
        this.messageQueue.unshift(...batch);
      });
    
    this.batchTimer = null;
  }
}
```

### Subscription Management

```javascript
class SubscriptionManager {
  constructor(socket) {
    this.socket = socket;
    this.subscriptions = new Map();
    this.refCounts = new Map();
  }
  
  subscribe(topic, handler) {
    const key = `${topic}:${handler.toString()}`;
    
    if (!this.subscriptions.has(topic)) {
      const channel = this.socket.channel(topic);
      this.subscriptions.set(topic, channel);
      this.refCounts.set(topic, 0);
      
      channel.join()
        .receive('ok', () => console.log(`Subscribed to ${topic}`));
    }
    
    const channel = this.subscriptions.get(topic);
    channel.on('update', handler);
    
    this.refCounts.set(topic, this.refCounts.get(topic) + 1);
    
    return () => this.unsubscribe(topic, handler);
  }
  
  unsubscribe(topic, handler) {
    const channel = this.subscriptions.get(topic);
    if (!channel) return;
    
    channel.off('update', handler);
    
    const refCount = this.refCounts.get(topic) - 1;
    this.refCounts.set(topic, refCount);
    
    if (refCount === 0) {
      channel.leave();
      this.subscriptions.delete(topic);
      this.refCounts.delete(topic);
      console.log(`Unsubscribed from ${topic}`);
    }
  }
}
```

## Client Libraries

### JavaScript/TypeScript

```typescript
// TypeScript types
interface ChannelMessage<T = any> {
  event: string;
  payload: T;
  ref?: string;
}

interface ChannelResponse<T = any> {
  status: 'ok' | 'error' | 'timeout';
  response: T;
}

class TypedChannel<T extends Record<string, any>> {
  private channel: Channel;
  
  constructor(socket: Socket, topic: string, params?: any) {
    this.channel = socket.channel(topic, params);
  }
  
  on<K extends keyof T>(event: K, callback: (payload: T[K]) => void): void {
    this.channel.on(event as string, callback);
  }
  
  push<K extends keyof T>(
    event: K,
    payload: T[K]
  ): Promise<ChannelResponse> {
    return new Promise((resolve) => {
      this.channel.push(event as string, payload)
        .receive('ok', (response) => resolve({ status: 'ok', response }))
        .receive('error', (response) => resolve({ status: 'error', response }))
        .receive('timeout', () => resolve({ status: 'timeout', response: null }));
    });
  }
}

// Usage
interface CaseChannelEvents {
  'document:uploaded': { document: Document };
  'workflow:started': { workflow_id: string; case_id: string };
  'add:document': { file: File; metadata: any };
}

const caseChannel = new TypedChannel<CaseChannelEvents>(socket, `case:${caseId}`);

caseChannel.on('document:uploaded', ({ document }) => {
  console.log('New document:', document);
});

await caseChannel.push('add:document', {
  file: selectedFile,
  metadata: { tags: ['important'] }
});
```

### Python

```python
import asyncio
import json
import websockets
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    JOIN = "phx_join"
    LEAVE = "phx_leave"
    REPLY = "phx_reply"
    ERROR = "phx_error"
    CLOSE = "phx_close"
    HEARTBEAT = "heartbeat"

@dataclass
class Message:
    topic: str
    event: str
    payload: Dict[str, Any]
    ref: Optional[str] = None
    join_ref: Optional[str] = None

class PhoenixChannel:
    def __init__(self, socket: 'PhoenixSocket', topic: str, params: Dict[str, Any] = None):
        self.socket = socket
        self.topic = topic
        self.params = params or {}
        self.join_ref = None
        self.callbacks: Dict[str, list[Callable]] = {}
        self.joined = False
        
    async def join(self):
        self.join_ref = self.socket.make_ref()
        message = Message(
            topic=self.topic,
            event=EventType.JOIN.value,
            payload=self.params,
            ref=self.socket.make_ref(),
            join_ref=self.join_ref
        )
        
        response = await self.socket.push_and_wait(message)
        if response.payload.get("status") == "ok":
            self.joined = True
            return response.payload.get("response", {})
        else:
            raise Exception(f"Failed to join channel: {response.payload}")
    
    def on(self, event: str, callback: Callable):
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
    
    async def push(self, event: str, payload: Dict[str, Any]):
        if not self.joined:
            raise Exception("Must join channel before pushing events")
            
        message = Message(
            topic=self.topic,
            event=event,
            payload=payload,
            ref=self.socket.make_ref(),
            join_ref=self.join_ref
        )
        
        return await self.socket.push_and_wait(message)
    
    def trigger(self, event: str, payload: Dict[str, Any]):
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                asyncio.create_task(callback(payload))

class PhoenixSocket:
    def __init__(self, url: str, params: Dict[str, Any] = None):
        self.url = url
        self.params = params or {}
        self.ws = None
        self.channels: Dict[str, PhoenixChannel] = {}
        self.ref_counter = 0
        self.pending_replies: Dict[str, asyncio.Future] = {}
        
    async def connect(self):
        url_with_params = f"{self.url}?{self._encode_params(self.params)}"
        self.ws = await websockets.connect(url_with_params)
        asyncio.create_task(self._receive_loop())
        asyncio.create_task(self._heartbeat_loop())
        
    async def _receive_loop(self):
        async for message in self.ws:
            data = json.loads(message)
            msg = Message(**data)
            
            # Handle replies
            if msg.ref and msg.ref in self.pending_replies:
                self.pending_replies[msg.ref].set_result(msg)
            
            # Route to channel
            if msg.topic in self.channels:
                self.channels[msg.topic].trigger(msg.event, msg.payload)
    
    async def push_and_wait(self, message: Message) -> Message:
        future = asyncio.Future()
        self.pending_replies[message.ref] = future
        
        await self.ws.send(json.dumps({
            "topic": message.topic,
            "event": message.event,
            "payload": message.payload,
            "ref": message.ref,
            "join_ref": message.join_ref
        }))
        
        try:
            return await asyncio.wait_for(future, timeout=5.0)
        except asyncio.TimeoutError:
            del self.pending_replies[message.ref]
            raise
    
    def channel(self, topic: str, params: Dict[str, Any] = None) -> PhoenixChannel:
        if topic not in self.channels:
            self.channels[topic] = PhoenixChannel(self, topic, params)
        return self.channels[topic]
    
    def make_ref(self) -> str:
        self.ref_counter += 1
        return str(self.ref_counter)

# Usage example
async def main():
    socket = PhoenixSocket(
        "wss://api.ediscovery-hypergraph.com/socket",
        {"token": "YOUR_TOKEN"}
    )
    
    await socket.connect()
    
    # Join case channel
    case_channel = socket.channel(f"case:{case_id}")
    await case_channel.join()
    
    # Listen for events
    case_channel.on("document:processed", lambda payload: 
        print(f"Document processed: {payload}")
    )
    
    # Push event
    response = await case_channel.push("request:summary", {
        "document_id": "doc_123"
    })
    
    print(f"Summary response: {response}")

asyncio.run(main())
```

## Security Considerations

### Message Validation

```javascript
// Client-side validation
function validateMessage(message) {
  // Check message structure
  if (!message.event || !message.payload) {
    throw new Error('Invalid message format');
  }
  
  // Validate payload size
  const payloadSize = JSON.stringify(message.payload).length;
  if (payloadSize > 65536) { // 64KB limit
    throw new Error('Payload too large');
  }
  
  // Sanitize user input
  if (message.payload.html) {
    message.payload.html = sanitizeHtml(message.payload.html);
  }
  
  return message;
}

// Rate limiting
class RateLimiter {
  constructor(maxRequests = 100, windowMs = 60000) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
    this.requests = [];
  }
  
  canSend() {
    const now = Date.now();
    this.requests = this.requests.filter(time => now - time < this.windowMs);
    
    if (this.requests.length >= this.maxRequests) {
      return false;
    }
    
    this.requests.push(now);
    return true;
  }
}

const rateLimiter = new RateLimiter();

channel.push = new Proxy(channel.push, {
  apply(target, thisArg, args) {
    if (!rateLimiter.canSend()) {
      throw new Error('Rate limit exceeded');
    }
    
    const [event, payload] = args;
    validateMessage({ event, payload });
    
    return target.apply(thisArg, args);
  }
});
```

### Encryption

```javascript
// End-to-end encryption for sensitive data
class EncryptedChannel {
  constructor(channel, encryptionKey) {
    this.channel = channel;
    this.encryptionKey = encryptionKey;
  }
  
  async push(event, payload) {
    const encrypted = await this.encrypt(payload);
    return this.channel.push(event, { encrypted });
  }
  
  on(event, callback) {
    this.channel.on(event, async (payload) => {
      if (payload.encrypted) {
        const decrypted = await this.decrypt(payload.encrypted);
        callback(decrypted);
      } else {
        callback(payload);
      }
    });
  }
  
  async encrypt(data) {
    const iv = crypto.getRandomValues(new Uint8Array(16));
    const encoded = new TextEncoder().encode(JSON.stringify(data));
    
    const encrypted = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      this.encryptionKey,
      encoded
    );
    
    return {
      iv: Array.from(iv),
      data: Array.from(new Uint8Array(encrypted))
    };
  }
  
  async decrypt(encrypted) {
    const decrypted = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: new Uint8Array(encrypted.iv) },
      this.encryptionKey,
      new Uint8Array(encrypted.data)
    );
    
    const decoded = new TextDecoder().decode(decrypted);
    return JSON.parse(decoded);
  }
}
```

## Next Steps

- Review [REST API](/api/rest-api) for request-response operations
- Explore [GraphQL API](/api/graphql-api) for complex queries
- Check [Examples](/examples) for real-world implementations
- Visit [Support](/support) for troubleshooting help