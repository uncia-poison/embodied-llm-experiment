# Hosted run requests

A YAML file committed directly under this directory can trigger the private `Hosted LLM experiment`
workflow. Request files contain no credentials and are intentionally retained as an audit trail.

Example:

```yaml
schema_version: 1
request_id: deepseek-smoke-001
provider: deepseek
profile: smoke
purpose: Validate the hosted causal loop before a full episode
approved: true
```

Allowed providers are `deepseek` and `gemini`. Allowed profiles are `smoke` and `episode`.
The workflow maps these values to fixed repository configs; request files cannot execute arbitrary
commands or select arbitrary paths.

API keys must be stored only as repository Actions secrets named `DEEPSEEK_API_KEY` and
`GEMINI_API_KEY`. Never place a key in a request file, issue, commit, workflow input or chat message.
