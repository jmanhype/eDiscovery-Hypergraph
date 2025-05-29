# A2A Agent API Reference

This document describes the API endpoints and message protocols supported by the A2A Agent, including streaming and event-driven features.

---

## Endpoints

### 1. `/api/a2a` (POST)
- **Description:** Main endpoint for agent-to-agent protocol messages, including task requests, streaming, events, discovery, and negotiation.
- **Content-Type:** `application/json`

#### Supported Message Types

| Type              | Description                                              |
|-------------------|----------------------------------------------------------|
| `task_request`    | Request to execute a task graph (can be streamed)        |
| `task_progress`   | Progress update for a running task                       |
| `task_chunk`      | Partial (chunked) result for a running task              |
| `agent_event`     | Arbitrary agent-generated event                          |
| `agent_discovery` | Request list of available agents                         |
| `negotiation`     | Negotiation protocol for agent collaboration             |

---

### Message Schemas

#### 1. `task_request`
```json
{
  "type": "task_request",
  "sender": "agent1",
  "recipient": "agent2",
  "payload": {
    "graph": {"nodes": [...], "edges": [...]},
    "agent_map": {...},
    "input": {...},
    "stream": true,         // Optional: enables streaming
    "task_id": "xyz"        // Optional: for tracking
  }
}
```
- **Response:**
  - If `stream: true`, response is a chunked stream of `task_chunk` JSON objects.
  - Otherwise, response is `{ "status": "ok", "result": ... }` or error.

#### 2. `task_progress`
```json
{
  "type": "task_progress",
  "task_id": "xyz",
  "payload": {
    "progress": 42,      // percent or step
    "message": "Halfway done"
  },
  "sender": "agent1",
  "recipient": "agent2"
}
```
- **Response:** `{ "status": "ok", "type": "task_progress", "task_id": "xyz", "progress": ... }`

#### 3. `task_chunk`
```json
{
  "type": "task_chunk",
  "task_id": "xyz",
  "payload": {
    "data": "partial result..."
  },
  "sender": "agent1",
  "recipient": "agent2"
}
```
- **Response:** `{ "status": "ok", "type": "task_chunk", "task_id": "xyz", "chunk": ... }`

#### 4. `agent_event`
```json
{
  "type": "agent_event",
  "event_id": "evt-123",
  "payload": {
    "event_type": "log",
    "message": "Agent started"
  },
  "sender": "agent1",
  "recipient": "agent2"
}
```
- **Response:** `{ "status": "ok", "type": "agent_event", "event_id": "evt-123", "event": ... }`

#### 5. `agent_discovery`
```json
{
  "type": "agent_discovery",
  "sender": "agent1",
  "recipient": "agent2",
  "payload": {}
}
```
- **Response:** `{ "status": "ok", "agents": [ ...AgentCard... ] }`

#### 6. `negotiation`
```json
{
  "type": "negotiation",
  "sender": "agent1",
  "recipient": "agent2",
  "payload": {
    "proposal": "...",
    "details": {...}
  }
}
```
- **Response:** `{ "status": "accepted"|"rejected", "reason": "..." }`

---

### Streaming Responses
- If a `task_request` is sent with `"stream": true`, the response will be a chunked HTTP stream of JSON objects, each representing a `task_chunk`.
- Example streamed response:
```
{"type": "task_chunk", "task_id": "xyz", "chunk": 1, "payload": {"data": "partial_result_1"}}
{"type": "task_chunk", "task_id": "xyz", "chunk": 2, "payload": {"data": "partial_result_2"}}
...
```

---

### Error Responses
All errors follow this structure:
```json
{
  "status": "error",
  "error": "Description of the error"
}
```

---

## Example Usage

#### 1. Submit a streaming task request
```sh
curl -X POST http://localhost:4000/api/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "type": "task_request",
    "sender": "agent1",
    "recipient": "agent2",
    "payload": {
      "graph": {"nodes": [], "edges": []},
      "agent_map": {},
      "input": {},
      "stream": true
    }
  }'
```

#### 2. Send a progress update
```sh
curl -X POST http://localhost:4000/api/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "type": "task_progress",
    "task_id": "xyz",
    "payload": {"progress": 50, "message": "Halfway"},
    "sender": "agent1",
    "recipient": "agent2"
  }'
```

---

## AgentCard Schema

The `agents` field in `agent_discovery` responses returns a list of AgentCard objects:
```json
{
  "id": "agent1",
  "name": "A2A Agent",
  "version": "0.1.0",
  "description": "Phoenix A2A agent interface",
  "capabilities": ["task_request", "negotiation", ...],
  "endpoints": {"a2a": "/api/a2a", ...},
  "authentication": null
}
```

---

## Notes
- All requests and responses are JSON.
- For streaming, use HTTP clients that support chunked responses.
- Extendable: add more event types as needed.

---

For further questions or to propose protocol extensions, see the source code or contact the maintainers.
