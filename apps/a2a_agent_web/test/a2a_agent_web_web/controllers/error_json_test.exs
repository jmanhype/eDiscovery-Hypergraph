defmodule A2aAgentWebWeb.ErrorJSONTest do
  use A2aAgentWebWeb.ConnCase, async: true

  test "renders 404" do
    assert A2aAgentWebWeb.ErrorJSON.render("404.json", %{}) == %{errors: %{detail: "Not Found"}}
  end

  test "renders 500" do
    assert A2aAgentWebWeb.ErrorJSON.render("500.json", %{}) ==
             %{errors: %{detail: "Internal Server Error"}}
  end
end
