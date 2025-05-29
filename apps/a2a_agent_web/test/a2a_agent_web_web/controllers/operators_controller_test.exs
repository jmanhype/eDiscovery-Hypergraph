defmodule A2aAgentWebWeb.OperatorsControllerTest do
  @moduledoc """
  Tests for the /api/operators introspection endpoints.
  """
  use A2aAgentWebWeb.ConnCase, async: true

  import Phoenix.ConnTest

  test "GET /api/operators returns operator list", %{conn: conn} do
    conn = get(conn, "/api/operators")
    assert json_response(conn, 200)["operators"] == [
             "aggregate_operator",
             "branch_operator",
             "llm_operator",
             "map_operator",
             "parallel_operator",
             "sequence_operator"
           ]
  end

  test "GET /api/operators/:name returns details for known operator", %{conn: conn} do
    conn = get(conn, "/api/operators/llm_operator")
    body = json_response(conn, 200)
    assert body["name"] == "llm_operator"
    assert body["description"] == "Runs a language model with a given prompt."
  end

  test "GET /api/operators/:name returns error for unknown operator", %{conn: conn} do
    conn = get(conn, "/api/operators/unknown")
    body = json_response(conn, 200)
    assert body["name"] == "unknown"
    assert body["error"] == "Operator not found"
  end
end
