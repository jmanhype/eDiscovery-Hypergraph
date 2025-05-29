defmodule A2aAgentWebWeb.ModelsControllerTest do
  @moduledoc """
  Tests for the ModelsController model introspection endpoint.
  """
  use A2aAgentWebWeb.ConnCase, async: true

  @doc """
  GET /api/models returns a list of models and metadata.
  """
  test "GET /api/models returns list of models", %{conn: conn} do
    conn = get(conn, "/api/models")
    expected =
      HypergraphAgent.Models.list_models()
      |> Enum.map(fn m -> for {k, v} <- m, into: %{}, do: {to_string(k), v} end)
    assert json_response(conn, 200) == expected
  end
end
