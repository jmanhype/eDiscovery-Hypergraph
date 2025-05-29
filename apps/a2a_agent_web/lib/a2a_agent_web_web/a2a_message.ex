defmodule A2aAgentWebWeb.A2AMessage do
  @moduledoc """
  Struct and validation for A2A agent messages.
  """
  @enforce_keys [:type, :sender, :recipient, :payload]
  defstruct [
    :type,        # :task_request | :result | :status_update | ...
    :sender,      # agent id or card
    :recipient,   # agent id or card
    :payload,     # map, task or result data
    :task_id,     # optional
    :timestamp    # optional
  ]

  @type t :: %__MODULE__{
          type: atom(),
          sender: String.t(),
          recipient: String.t(),
          payload: map(),
          task_id: String.t() | nil,
          timestamp: String.t() | nil
        }

  @allowed_types [:task_request, :result, :status_update, :agent_discovery, :negotiation]

  @spec validate(map()) :: {:ok, t()} | {:error, String.t()}
  def validate(params) when is_map(params) do
    required = ["type", "sender", "recipient", "payload"]
    missing = Enum.filter(required, &(!Map.has_key?(params, &1)))
    if missing != [] do
      {:error, "Missing required fields: #{Enum.join(missing, ", " )}"}
    else
      type = parse_type(params["type"])
      if type in @allowed_types do
        {:ok, %__MODULE__{
          type: type,
          sender: params["sender"],
          recipient: params["recipient"],
          payload: params["payload"] || %{},
          task_id: Map.get(params, "task_id"),
          timestamp: Map.get(params, "timestamp")
        }}
      else
        {:error, "Invalid type: #{inspect(params["type"])}. Allowed types: #{inspect(@allowed_types)}"}
      end
    end
  end

  defp parse_type(type) when is_atom(type), do: type
  defp parse_type(type) when is_binary(type) do
    case Enum.find(@allowed_types, fn allowed -> Atom.to_string(allowed) == type end) do
      nil -> nil
      atom -> atom
    end
  end
  defp parse_type(_), do: nil
end
