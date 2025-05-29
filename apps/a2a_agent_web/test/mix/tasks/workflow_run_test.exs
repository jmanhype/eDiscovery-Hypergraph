defmodule Mix.Tasks.Workflow.RunTest do
  @moduledoc """
  Tests for the workflow.run Mix task CLI.
  """
  use ExUnit.Case, async: false
  import ExUnit.CaptureIO

  @yaml Path.expand("../../../workflows/summarize_and_analyze.yaml", __DIR__)
  @input_kv "text=Elixir"
  @input_json ~s({"text":"Elixir JSON"})
  @output_file "tmp/workflow_result.json"

  setup_all do
    File.mkdir_p!("tmp")
    on_exit(fn -> File.rm_rf!("tmp") end)
    :ok
  end

  test "runs workflow with --input key-value" do
    output =
      capture_io(fn ->
        Mix.Tasks.Workflow.Run.run([@yaml, "--input", @input_kv])
      end)

    assert output =~ "Workflow result:"
    assert output =~ "Elixir"
  end

  test "runs workflow with --json input" do
    output =
      capture_io(fn ->
        Mix.Tasks.Workflow.Run.run([@yaml, "--json", @input_json])
      end)

    assert output =~ "Workflow result:"
    # Robustly extract all JSON objects from output and find the workflow result
    jsons = Regex.scan(~r/(\{(?:[^{}]|(?1))*\})/, output) |> Enum.map(&List.first/1)
    result =
      Enum.find_value(jsons, fn json ->
        case Jason.decode(json) do
          {:ok, %{"summarize" => _, "analyze" => _} = result} -> result
          _ -> nil
        end
      end) || flunk("Could not find workflow result JSON in: #{output}")
    # Assert the expected structure and values
    assert Map.has_key?(result, "summarize")
    assert Map.has_key?(result, "analyze")
    assert String.contains?(result["summarize"]["result"], "Elixir")
    assert String.contains?(result["analyze"]["result"], "Elixir")
  end

  test "writes output to file with --output" do
    path = @output_file
    capture_io(fn ->
      Mix.Tasks.Workflow.Run.run([@yaml, "--json", @input_json, "--output", path])
    end)
    assert File.exists?(path)
    content = File.read!(path)
    {:ok, result} = Jason.decode(content)
    assert Map.has_key?(result, "summarize")
    assert Map.has_key?(result, "analyze")
    assert String.contains?(result["summarize"]["result"], "Elixir")
    assert String.contains?(result["analyze"]["result"], "Elixir")
  end

  test "fails gracefully on invalid JSON" do
    assert_raise Mix.Error, fn ->
      capture_io(fn ->
        Mix.Tasks.Workflow.Run.run([@yaml, "--json", "{invalid"])
      end)
    end
  end

  test "fails gracefully on invalid YAML" do
    assert capture_io(fn ->
      Mix.Tasks.Workflow.Run.run(["does_not_exist.yaml"])
    end) =~ "Workflow failed"
  end
end
