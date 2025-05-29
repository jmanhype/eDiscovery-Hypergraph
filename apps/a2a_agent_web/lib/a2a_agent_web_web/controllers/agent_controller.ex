defmodule A2aAgentWebWeb.AgentController do
  use A2aAgentWebWeb, :controller
  require Logger

  @doc """
  Returns this agent's card for discovery (local agent).
  """
  def agent_card(conn, _params) do
    card = A2aAgentWebWeb.AgentCard.build()
    json(conn, card)
  end

  @doc """
  Registers a remote agent card (POST /api/agent_card).
  """
  def register_agent(conn, params) do
    with {:ok, card} <- cast_card(params) do
      A2aAgentWebWeb.AgentRegistry.register_agent(card)
      json(conn, %{status: "ok", agent: card})
    else
      {:error, reason} ->
        conn |> put_status(:bad_request) |> json(%{status: "error", error: reason})
    end
  end

  @doc """
  Unregisters an agent by id (DELETE /api/agent_card/:id).
  Returns 200 and status "ok" if the agent was unregistered, or 404 and status "error" if not found.
  """
  @spec unregister_agent(Plug.Conn.t(), map()) :: Plug.Conn.t()
  def unregister_agent(conn, %{"id" => id}) do
    require Logger
    case A2aAgentWebWeb.AgentRegistry.get_agent(id) do
      nil ->
        Logger.warn("Attempted to unregister non-existent agent: #{inspect(id)}")
        conn
        |> Plug.Conn.put_status(:not_found)
        |> json(%{status: "error", error: "Agent not found", id: id})
      _card ->
        :ok = A2aAgentWebWeb.AgentRegistry.unregister_agent(id)
        Logger.info("Unregistered agent: #{inspect(id)}")
        conn
        |> json(%{status: "ok", id: id})
    end
  end

  @doc """
  Lists all registered agent cards (GET /api/agent_registry).
  """
  def list_agents(conn, _params) do
    agents = A2aAgentWebWeb.AgentRegistry.list_agents()
    json(conn, agents)
  end

  @doc """
  Gets a specific agent card by id (GET /api/agent_card/:id).
  """
  def get_agent(conn, %{"id" => id}) do
    case A2aAgentWebWeb.AgentRegistry.get_agent(id) do
      nil -> conn |> put_status(:not_found) |> json(%{status: "error", error: "Not found"})
      card -> json(conn, card)
    end
  end

  # Helper to cast params to AgentCard struct
  @spec cast_card(map()) :: {:ok, A2aAgentWebWeb.AgentCard.t()} | {:error, String.t()}
  defp cast_card(params) do
    try do
      atom_params =
        Enum.reduce(params, %{}, fn {k, v}, acc ->
          key = if is_atom(k), do: k, else: String.to_atom(k)
          Map.put(acc, key, v)
        end)
      {:ok, struct!(A2aAgentWebWeb.AgentCard, atom_params)}
    rescue
      _ -> {:error, "Invalid agent card params"}
    end
  end

  @doc """
  Receives and validates A2A messages, then invokes orchestrator if valid.
  Expects JSON body matching A2AMessage schema.
  """
  @spec a2a(Plug.Conn.t(), map()) :: Plug.Conn.t()
  def a2a(conn, params) do
    require OpenTelemetry.Tracer
    OpenTelemetry.Tracer.with_span "A2A Agent a2a request" do
      start_time = System.monotonic_time(:microsecond)
      req_type =
        case params["type"] do
          t when is_binary(t) -> t
          t when is_atom(t) -> Atom.to_string(t)
          _ -> "unknown"
        end
      agent_id = params["sender"] || "unknown"
      OpenTelemetry.Tracer.set_attribute("a2a.type", req_type)
      OpenTelemetry.Tracer.set_attribute("a2a.agent_id", agent_id)
      req_size =
        try do
          byte_size(Jason.encode!(params))
        rescue
          _ -> 0
        end
      A2aAgentWebWeb.Metrics.observe_size(req_type, req_size)
      event = GreEx.make([event: :message_received, type: req_type, agent_id: agent_id])
      GoldrushEx.handle(:message_received_handler, event)
      case A2aAgentWebWeb.A2AMessage.validate(params) do
        {:ok, msg} ->
          type_str = to_string(msg.type)
          case type_str do
            "negotiation" ->
              A2aAgentWebWeb.Metrics.inc_message("negotiation")
              Logger.info("Received negotiation message: #{inspect(msg)}")
              case A2aAgentWebWeb.NegotiationHandler.negotiate(msg.payload) do
                {:accepted, reason} ->
                  latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
                  A2aAgentWebWeb.Metrics.observe_latency("negotiation", latency)
                  A2aAgentWebWeb.Metrics.inc_negotiation("accepted")
                  json(conn, %{status: "accepted", reason: reason})
                {:rejected, reason} ->
                  latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
                  A2aAgentWebWeb.Metrics.observe_latency("negotiation", latency)
                  A2aAgentWebWeb.Metrics.inc_negotiation("rejected")
                  json(conn, %{status: "rejected", reason: reason})
                other ->
                  latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
                  A2aAgentWebWeb.Metrics.observe_latency("negotiation", latency)
                  A2aAgentWebWeb.Metrics.inc_negotiation("rejected")
                  json(conn, %{status: "rejected", reason: inspect(other)})
              end
            "agent_discovery" ->
              A2aAgentWebWeb.Metrics.inc_message("agent_discovery")
              Logger.info("Received agent_discovery message: #{inspect(msg)}")
              event = GreEx.make([event: :task_started, task_id: "agent_discovery", agent_id: agent_id])
              GoldrushEx.handle(:task_started_handler, event)
              agents = A2aAgentWebWeb.AgentRegistry.list_agents() || []
              latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
              A2aAgentWebWeb.Metrics.observe_latency("agent_discovery", latency)
              json(conn, %{status: "ok", agents: agents})
            _ ->
              msg_type = type_str
              A2aAgentWebWeb.Metrics.inc_message(msg_type)
              Logger.info("Received other message type: #{inspect(msg.type)}")
              event = GreEx.make([event: :task_started, task_id: msg_type, agent_id: agent_id])
              GoldrushEx.handle(:task_started_handler, event)
              latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
              A2aAgentWebWeb.Metrics.observe_latency(msg_type, latency)
              json(conn, %{status: "ok", info: "Message type handled: #{inspect(msg.type)} (stub)"})
          end

        {:ok, %{type: :task_request, payload: payload} = _msg} when is_map(payload) ->
          if Map.get(payload, "stream", false) == true do
            A2aAgentWebWeb.Metrics.inc_message("task_request_stream")
            conn = conn
              |> put_resp_content_type("application/json")
              |> send_chunked(200)
            # Simulate streaming chunks (replace with real orchestrator streaming in production)
            Enum.reduce(1..5, conn, fn i, conn_acc ->
              chunk = %{type: "task_chunk", task_id: payload["task_id"] || "streamed_task", chunk: i, payload: %{data: "partial_result_#{i}"}}
              {:ok, _} = chunk(conn_acc, Jason.encode!(chunk) <> "\n")
              :timer.sleep(100)
              conn_acc
            end)
          else
            # Standard (non-streaming) task_request
            A2aAgentWebWeb.Metrics.inc_message("task_request")
            if Map.has_key?(payload, "graph") and Map.has_key?(payload, "agent_map") and Map.has_key?(payload, "input") do
              A2aAgentWebWeb.Metrics.inc_orchestration()
              case HypergraphAgent.BasicOrchestrator.orchestrate(payload["graph"], payload["agent_map"], payload["input"], []) do
                {:ok, result} ->
                  latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
                  A2aAgentWebWeb.Metrics.observe_latency("task_request", latency)
                  json(conn, %{status: "ok", result: result})
                {:error, reason} ->
                  latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
                  A2aAgentWebWeb.Metrics.observe_latency("task_request", latency)
                  OpenTelemetry.Tracer.set_attribute("a2a.error_type", "orchestrate_error")
                  A2aAgentWebWeb.Metrics.inc_error("orchestrate_error")
                  conn
                  |> put_status(:internal_server_error)
                  |> json(%{status: "error", error: inspect(reason)})
                other ->
                  latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
                  A2aAgentWebWeb.Metrics.observe_latency("task_request", latency)
                  OpenTelemetry.Tracer.set_attribute("a2a.error_type", "internal_error")
                  A2aAgentWebWeb.Metrics.inc_error("internal_error")
                  conn
                  |> put_status(:internal_server_error)
                  |> json(%{status: "error", error: inspect(other)})
              end
            else
              latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
              A2aAgentWebWeb.Metrics.observe_latency("task_request", latency)
              OpenTelemetry.Tracer.set_attribute("a2a.error_type", "missing_fields")
              A2aAgentWebWeb.Metrics.inc_error("missing_fields")
              conn
              |> put_status(:bad_request)
              |> json(%{status: "error", error: "Payload missing required fields: graph, agent_map, input"})
            end
          end

          A2aAgentWebWeb.Metrics.inc_message("task_request")
          if Map.has_key?(payload, "graph") and Map.has_key?(payload, "agent_map") and Map.has_key?(payload, "input") do
            A2aAgentWebWeb.Metrics.inc_orchestration()
            case HypergraphAgent.BasicOrchestrator.orchestrate(payload["graph"], payload["agent_map"], payload["input"], []) do
              {:ok, result} ->
                latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
                A2aAgentWebWeb.Metrics.observe_latency("task_request", latency)
                json(conn, %{status: "ok", result: result})
              {:error, reason} ->
                latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
                A2aAgentWebWeb.Metrics.observe_latency("task_request", latency)
                OpenTelemetry.Tracer.set_attribute("a2a.error_type", "orchestrate_error")
                A2aAgentWebWeb.Metrics.inc_error("orchestrate_error")
                conn
                |> put_status(:internal_server_error)
                |> json(%{status: "error", error: inspect(reason)})
              other ->
                latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
                A2aAgentWebWeb.Metrics.observe_latency("task_request", latency)
                OpenTelemetry.Tracer.set_attribute("a2a.error_type", "internal_error")
                A2aAgentWebWeb.Metrics.inc_error("internal_error")
                conn
                |> put_status(:internal_server_error)
                |> json(%{status: "error", error: inspect(other)})
            end
          else
            latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
            A2aAgentWebWeb.Metrics.observe_latency("task_request", latency)
            OpenTelemetry.Tracer.set_attribute("a2a.error_type", "missing_fields")
            A2aAgentWebWeb.Metrics.inc_error("missing_fields")
            conn
            |> put_status(:bad_request)
            |> json(%{status: "error", error: "Payload missing required fields: graph, agent_map, input"})
          end
        # Streaming/event message types
        {:ok, %{type: :task_progress, task_id: tid, payload: payload}} ->
          # Broadcast or log progress event
          Logger.info("Task progress event for #{tid}: #{inspect(payload)}")
          json(conn, %{status: "ok", type: "task_progress", task_id: tid, progress: payload})
        {:ok, %{type: :task_chunk, task_id: tid, payload: payload}} ->
          # Broadcast or log chunk event
          Logger.info("Task chunk event for #{tid}: #{inspect(payload)}")
          json(conn, %{status: "ok", type: "task_chunk", task_id: tid, chunk: payload})

        # Accept both atom and string for type field
        {:ok, %{type: type} = msg} when type in [:agent_discovery, "agent_discovery"] ->
          A2aAgentWebWeb.Metrics.inc_message("agent_discovery")
          Logger.info("Received agent_discovery message: #{inspect(msg)}")
          event = GreEx.make([event: :task_started, task_id: "agent_discovery", agent_id: agent_id])
          GoldrushEx.handle(:task_started_handler, event)
          agents = A2aAgentWebWeb.AgentRegistry.list_agents() || []
          latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
          A2aAgentWebWeb.Metrics.observe_latency("agent_discovery", latency)
          json(conn, %{status: "ok", agents: agents})
        # Accept both atom and string for type field
        {:ok, %{type: type, payload: payload} = msg} when type in [:negotiation, "negotiation"] ->
          A2aAgentWebWeb.Metrics.inc_message("negotiation")
          Logger.info("Received negotiation message: #{inspect(msg)}")
          case A2aAgentWebWeb.NegotiationHandler.negotiate(payload) do
            {:accepted, reason} ->
              latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
              A2aAgentWebWeb.Metrics.observe_latency("negotiation", latency)
              A2aAgentWebWeb.Metrics.inc_negotiation("accepted")
              json(conn, %{status: "accepted", reason: reason})
            {:rejected, reason} ->
              latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
              A2aAgentWebWeb.Metrics.observe_latency("negotiation", latency)
              A2aAgentWebWeb.Metrics.inc_negotiation("rejected")
              json(conn, %{status: "rejected", reason: reason})
            other ->
              latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
              A2aAgentWebWeb.Metrics.observe_latency("negotiation", latency)
              A2aAgentWebWeb.Metrics.inc_negotiation("rejected")
              json(conn, %{status: "rejected", reason: inspect(other)})
          end

        # Fallback for negotiation with malformed payload
        {:ok, %{type: type}} when type in [:negotiation, "negotiation"] ->
          latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
          A2aAgentWebWeb.Metrics.observe_latency("negotiation", latency)
          A2aAgentWebWeb.Metrics.inc_negotiation("rejected")
          json(conn, %{status: "rejected", reason: "Invalid negotiation payload"})

        {:ok, msg} ->
          msg_type = to_string(msg.type)
          A2aAgentWebWeb.Metrics.inc_message(msg_type)
          Logger.info("Received other message type: #{inspect(msg.type)}")
          event = GreEx.make([event: :task_started, task_id: msg_type, agent_id: agent_id])
          GoldrushEx.handle(:task_started_handler, event)
          latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
          A2aAgentWebWeb.Metrics.observe_latency(msg_type, latency)
          json(conn, %{status: "ok", info: "Message type handled: #{inspect(msg.type)} (stub)"})
        {:error, reason} ->
          latency = (System.monotonic_time(:microsecond) - start_time) / 1_000_000
          A2aAgentWebWeb.Metrics.observe_latency(req_type, latency)
          OpenTelemetry.Tracer.set_attribute("a2a.error_type", "validation_error")
          A2aAgentWebWeb.Metrics.inc_error("validation_error")
          event = GreEx.make([event: :error_occurred, error: reason, agent_id: agent_id])
          GoldrushEx.handle(:error_occurred_handler, event)
          conn
          |> put_status(:bad_request)
          |> json(%{status: "error", error: reason})
      end
    end
  end
end
