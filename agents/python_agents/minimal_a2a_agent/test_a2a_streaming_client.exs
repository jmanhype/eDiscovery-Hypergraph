#!/usr/bin/env elixir
# File: test_a2a_streaming_client.exs

# Minimal Elixir script to send a streaming A2A task_request to a Python agent and print each chunked response.

Mix.install([:httpoison, :jason])

url = "http://localhost:5001/api/a2a"

body = %{
  type: "task_request",
  sender: "agent1",
  recipient: "pyagent1",
  payload: %{task_id: "t1", stream: true}
} |> Jason.encode!()

headers = [
  {"Content-Type", "application/json"}
]

IO.puts("Sending streaming request to #{url}...\n")

case HTTPoison.post(url, body, headers, stream_to: self(), recv_timeout: 10_000) do
  {:ok, resp} ->
    stream_chunks = fn stream_chunks ->
      receive do
        msg = %{__struct__: struct} ->
          struct_str = Atom.to_string(struct)
          cond do
            String.contains?(struct_str, "AsyncChunk") ->
              IO.puts(String.trim(msg.chunk))
              stream_chunks.(stream_chunks)
            String.contains?(struct_str, "AsyncEnd") ->
              IO.puts("\n[done]")
            String.contains?(struct_str, "AsyncStatus") ->
              IO.puts("[status: #{msg.code}]")
              stream_chunks.(stream_chunks)
            String.contains?(struct_str, "AsyncHeaders") ->
              stream_chunks.(stream_chunks)
            true ->
              IO.inspect(msg, label: "Unknown async message")
              stream_chunks.(stream_chunks)
          end
      after
        10_000 -> IO.puts("[timeout]")
      end
    end
    stream_chunks.(stream_chunks)
  {:error, err} ->
    IO.inspect(err, label: "HTTPoison error")
end

