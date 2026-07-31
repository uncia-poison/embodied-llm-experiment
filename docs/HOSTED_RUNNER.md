# Hosted model runner

The hosted runner lets GitHub Actions execute the embodied experiment against DeepSeek or Gemini
without manual copy/paste. The simulator, memory, interventions, causal counterfactuals, probes and
logging all run inside one private workflow job.

## Credentials

Add API keys as repository Actions secrets:

- `DEEPSEEK_API_KEY`
- `GEMINI_API_KEY`

Do not paste keys into source files, YAML run requests, issues, pull requests, workflow inputs or chat
messages. The workflow exposes each secret only as an environment variable to the model adapter.

## Starting a run

There are two supported entry points.

### GitHub Actions button

Open **Actions → Hosted LLM experiment → Run workflow**, choose a provider and profile, then type
`RUN` in the acknowledgement field. This is useful for a human-initiated paid call.

### Audited request commit

Commit a YAML file directly under `run-requests/`. This path is designed so an authorized automation
or repository agent can initiate the experiment without handling the API key.

```yaml
schema_version: 1
request_id: gemini-smoke-001
provider: gemini
profile: smoke
purpose: Validate the hosted transport and logging path
approved: true
```

The resolver accepts only four fixed combinations:

- `deepseek / smoke`
- `deepseek / episode`
- `gemini / smoke`
- `gemini / episode`

It maps them to repository-owned configs. A request file cannot inject a shell command or arbitrary
config path.

## Profiles

`smoke` is a six-tick, low-cost transport and protocol check. It includes coupled, disconnected and
remapped segments plus prediction and agency probes.

`episode` uses the longer provider profile with the full exploratory intervention schedule. It should
be run only after the corresponding smoke artifact has been inspected.

The provider profiles currently target `deepseek-v4-flash` through DeepSeek's OpenAI-compatible
`/chat/completions` endpoint and `gemini-3.6-flash` through Google's native `generateContent`
endpoint. Model identifiers remain in YAML so catalogue changes do not require runtime redesign.

## Artifacts and documentation

Every workflow attempt uploads one private artifact retained for 90 days. It contains:

- immutable launch metadata and the exact effective config;
- preflight JSON and stderr;
- console summary and experiment stderr;
- full run directories with `manifest.json`, `events.jsonl`, `probes.jsonl`, `summary.json` and any
  `failure.json`;
- a Markdown report with metrics, intervention segments, the complete utterance trajectory and probe
  calibration table.

The report is also written to the GitHub Actions job summary. Full prompts, raw responses, hidden
mappings, actions and counterfactual states remain in the private artifact rather than being printed
into the ordinary Actions log.

## Failure behavior

Artifacts are uploaded even when endpoint validation or inference fails. The final workflow status
then reflects the experiment exit code. This preserves partial trajectories and diagnostic evidence
without falsely marking an incomplete run as successful.

## Scientific boundary

A hosted web API gives a repeatable transport and explicit model identifier, but it is still a
black-box service whose weights and serving stack are controlled by the provider. Hosted results are
therefore stronger than manual web-chat relay runs for quantitative comparison, but model-version,
request-shape and date provenance must remain attached to every claim.
