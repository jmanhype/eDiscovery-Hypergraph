defmodule A2aAgentWebWeb.NegotiationHandler do
  @moduledoc """
  Simple negotiation handler for demonstration.
  Accepts proposals containing "foo", rejects others.
  """

  @doc """
  Processes a negotiation payload and returns {:accepted | :rejected, reason}.
  """
  @spec negotiate(map()) :: {:accepted | :rejected, String.t()}
  def negotiate(%{"proposal" => proposal}) when is_binary(proposal) do
    if String.contains?(proposal, "foo") do
      {:accepted, "Proposal accepted."}
    else
      {:rejected, "Proposal rejected: must contain 'foo'."}
    end
  end
  def negotiate(_), do: {:rejected, "Invalid negotiation payload."}
end
