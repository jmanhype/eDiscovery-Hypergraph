import httpx
import json

ELIXIR_AGENT_URL = "http://localhost:4000/api/a2a"
PYTHON_AGENT_URL = "http://localhost:5001/api/a2a"

# Example task_request message (with streaming enabled)
A2A_MSG = {
    "type": "task_request",
    "sender": "pyagent1",
    "recipient": "agent1",
    "payload": {
        "task_id": "t1",
        "stream": True
    }
}

def send_streaming_request(url: str, msg: dict):
    print(f"Sending streaming request to {url}...")
    with httpx.stream("POST", url, json=msg, timeout=10.0) as r:
        print(f"[status: {r.status_code}]")
        for line in r.iter_lines():
            if line:
                print(line)

def send_normal_request(url: str, msg: dict):
    print(f"Sending normal request to {url}...")
    r = httpx.post(url, json=msg, timeout=10.0)
    print(f"[status: {r.status_code}]")
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)

if __name__ == "__main__":
    # Test Python agent: task_request streaming
    send_streaming_request(PYTHON_AGENT_URL, A2A_MSG)

    # Test task_chunk streaming
    chunk_msg = {
        "type": "task_chunk",
        "sender": "pyagent1",
        "recipient": "agent1",
        "payload": {"chunk_id": "c1"}
    }
    send_streaming_request(PYTHON_AGENT_URL, chunk_msg)

    # Test agent_event (immediate/logged)
    event_msg = {
        "type": "agent_event",
        "sender": "pyagent1",
        "recipient": "agent1",
        "payload": {"event_id": "e1", "detail": "test event"}
    }
    send_normal_request(PYTHON_AGENT_URL, event_msg)

    # Negative test 1: missing 'type' key
    invalid_msg1 = {
        "sender": "pyagent1",
        "recipient": "agent1",
        "payload": {}
    }
    print("\n[Negative Test 1: missing 'type' key]")
    send_normal_request(PYTHON_AGENT_URL, invalid_msg1)

    # Negative test 2: 'type' is None
    invalid_msg2 = {
        "type": None,
        "sender": "pyagent1",
        "recipient": "agent1",
        "payload": {}
    }
    print("\n[Negative Test 2: 'type' is None]")
    send_normal_request(PYTHON_AGENT_URL, invalid_msg2)

    # Negative test 3: 'type' is not a string
    invalid_msg3 = {
        "type": 123,
        "sender": "pyagent1",
        "recipient": "agent1",
        "payload": {}
    }
    print("\n[Negative Test 3: 'type' is not a string]")
    send_normal_request(PYTHON_AGENT_URL, invalid_msg3)

    # Test normal request to Python agent
    A2A_MSG["payload"]["stream"] = False
    send_normal_request(PYTHON_AGENT_URL, A2A_MSG)
