defmodule A2aAgentWebWeb.ModelsController do
  @moduledoc """
  Controller for model introspection endpoint.
  Lists all available models and their metadata via /api/models.
  """
  use A2aAgentWebWeb, :controller

  @doc """
  Lists all available models and their metadata.
  """
  @spec index(Plug.Conn.t(), map()) :: Plug.Conn.t()
  def index(conn, _params) do
    models = HypergraphAgent.Models.list_models()
    json(conn, models)
  end
end
