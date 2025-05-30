defmodule A2aAgentWebWeb.SwaggerUiController do
  @moduledoc """
  Serves the Swagger UI for the A2A Agent Web API, referencing the live OpenAPI spec.
  """
  use A2aAgentWebWeb, :controller

  @doc """
  Renders the Swagger UI HTML, referencing /api/openapi.yaml.
  """
  @spec index(Plug.Conn.t(), map()) :: Plug.Conn.t()
  def index(conn, _params) do
    html = """
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
      <meta charset=\"UTF-8\">
      <title>Swagger UI - A2A Agent Web API</title>
      <link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist/swagger-ui.css\" />
    </head>
    <body>
      <div id=\"swagger-ui\"></div>
      <script src=\"https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js\"></script>
      <script>
        window.onload = function() {
          SwaggerUIBundle({
            url: '/api/openapi.yaml',
            dom_id: '#swagger-ui',
            presets: [SwaggerUIBundle.presets.apis],
            layout: 'BaseLayout',
            deepLinking: true
          });
        }
      </script>
    </body>
    </html>
    """
    send_resp(conn, 200, html)
  end
end
