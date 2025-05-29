import A2AAgentWeb.WorkflowDSL

workflow do
  node :summarize, LLMOperator, prompt_template: "Summarize: ~s", context: [topic: "Elixir DSLs"]
  node :analyze, MapOperator, depends_on: [:summarize], function: &MyApp.Analytics.analyze/1
end
