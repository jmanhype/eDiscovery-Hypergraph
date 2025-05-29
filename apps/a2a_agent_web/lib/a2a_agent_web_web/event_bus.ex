defmodule A2aAgentWebWeb.EventBus do
  @moduledoc """
  Distributed event bus using NATS (via :gnat) for agent and workflow events.
  Provides publish/subscribe functions for scalable, decoupled event streaming.
  """

  use GenServer
  require Logger

  @nats_conn :a2a_nats
  @default_subject "a2a.events"

  # Public API

  @doc """
  Starts the EventBus GenServer and establishes NATS connection.
  """
  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  @doc """
  Publish an event to the default subject (topic).
  Event should be a map or struct; will be JSON-encoded.
  """
  @spec publish(map(), String.t()) :: :ok | {:error, any()}
  def publish(event, subject \\ @default_subject) when is_map(event) do
    payload = Jason.encode!(event)
    case Gnat.pub(@nats_conn, subject, payload) do
      :ok -> :ok
      err ->
        Logger.error("[EventBus] Failed to publish event: #{inspect(err)}")
        {:error, err}
    end
  end

  @doc """
  Subscribe to a subject (topic) and handle messages via handle_event/1 callback.
  """
  @spec subscribe(String.t()) :: :ok | {:error, any()}
  def subscribe(subject \\ @default_subject) do
    Gnat.sub(@nats_conn, self(), subject)
  end

  # GenServer callbacks

  @impl true
  @impl true
  def init(_opts) do
    Logger.info("[EventBus] Starting EventBus and connecting to NATS...")
    nats_conf = Application.get_env(:a2a_agent_web, :nats, [])
    Logger.info("[EventBus] NATS config: #{inspect(nats_conf)}")
    Logger.flush()
    IO.puts("[EventBus] NATS config: #{inspect(nats_conf)}")
    host = Keyword.get(nats_conf, :host, "localhost")
    port = Keyword.get(nats_conf, :port, 4222)
    conn_opts = %{name: @nats_conn, host: host, port: port}
    case Gnat.start_link(conn_opts) do
      {:ok, conn} ->
        try do
          Process.register(conn, @nats_conn)
          Logger.info("[EventBus] Connected to NATS at #{host}:#{port} and registered as :a2a_nats (pid: #{inspect(conn)})")
        rescue
          ArgumentError ->
            Logger.warn("[EventBus] :a2a_nats was already registered, skipping registration.")
        end
        {:ok, %{conn: conn}}
      {:error, reason} ->
        Logger.error("[EventBus] Failed to connect to NATS at #{host}:#{port} -- reason: #{inspect(reason)}")
        {:stop, reason}
    end
  end

  @impl true
  def handle_info({:msg, msg}, state) do
    # Handle incoming NATS message
    case Jason.decode(msg.body) do
      {:ok, event} ->
        handle_event(event)
      _ ->
        Logger.warning("[EventBus] Received invalid event payload: #{inspect(msg.body)}")
    end
    {:noreply, state}
  end

  # Default event handler (override as needed)
  @spec handle_event(map()) :: :ok
  def handle_event(event) do
    Logger.info("[EventBus] Received event: #{inspect(event)}")
    :ok
  end
end
