defmodule A2aAgentWeb.ErrorJSONTest do
  use A2aAgentWeb.ConnCase, async: true

  test "renders 404" do
    assert A2aAgentWeb.ErrorJSON.render("404.json", %{}) == %{errors: %{detail: "Not Found"}}
  end

  test "renders 500" do
    assert A2aAgentWeb.ErrorJSON.render("500.json", %{}) ==
             %{errors: %{detail: "Internal Server Error"}}
  end
end
