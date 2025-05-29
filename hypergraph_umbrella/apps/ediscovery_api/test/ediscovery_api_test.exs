defmodule EdiscoveryApiTest do
  use ExUnit.Case
  doctest EdiscoveryApi

  test "greets the world" do
    assert EdiscoveryApi.hello() == :world
  end
end
