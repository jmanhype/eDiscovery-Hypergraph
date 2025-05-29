defmodule HypergraphAgent do
  @moduledoc """
  Multi-agent protocol and sample agent for hypergraph system.
  """

  @callback act(map()) :: map()
end

defmodule HypergraphAgent.BasicAgent do
  @moduledoc """
  Example implementation of the HypergraphAgent behaviour.
  """
  @behaviour HypergraphAgent

  @impl true
  def act(input) do
    Map.put(input, :acted, true)
  end
end
