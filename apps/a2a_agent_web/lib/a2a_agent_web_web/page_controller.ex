defmodule A2aAgentWebWeb.PageController do
  @moduledoc """
  Handles requests to the root page ("/") of the application.
  """
  use A2aAgentWebWeb, :controller

  @doc """
  Renders a simple welcome message for the root path.
  """
  @spec index(Plug.Conn.t(), map()) :: Plug.Conn.t()
  def index(conn, _params) do
    text(conn, "Welcome to A2aAgentWeb!")
  end
end
