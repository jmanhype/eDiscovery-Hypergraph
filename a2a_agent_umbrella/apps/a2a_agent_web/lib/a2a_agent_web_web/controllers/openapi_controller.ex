defmodule A2aAgentWebWeb.OpenapiController do
  @moduledoc """
  Serves the OpenAPI (Swagger) YAML spec for the A2A Agent Web API.
  """
  use A2aAgentWebWeb, :controller

  @openapi_path Path.expand("../../../openapi.yaml", __DIR__)

  @doc """
  Serves the raw OpenAPI YAML file.
  """
  @spec spec(Plug.Conn.t(), map()) :: Plug.Conn.t()
  def spec(conn, _params) do
    case File.read(@openapi_path) do
      {:ok, yaml} ->
        conn
        |> put_resp_content_type("application/yaml")
        |> send_resp(200, yaml)
      {:error, _} ->
        send_resp(conn, 404, "OpenAPI spec not found")
    end
  end
end
