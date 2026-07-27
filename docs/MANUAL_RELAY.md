# Manual web-model relay

This mode runs the body, world, memory, interventions and logging locally while a human relays each
model call through an ordinary web chat such as DeepSeek or Gemini. It requires no API key.

It is intended for exploratory testing and demonstrations. It is not interchangeable with the
preregistered API/local-model battery because the web product may have undisclosed system prompts,
sampling settings, safety layers, memory features or model updates.

## Start a session

DeepSeek web profile:

```bash
embodied-llm doctor --config configs/manual/deepseek-web.yaml
embodied-llm run --config configs/manual/deepseek-web.yaml
```

Gemini web profile:

```bash
embodied-llm doctor --config configs/manual/gemini-web.yaml
embodied-llm run --config configs/manual/gemini-web.yaml
```

The terminal prints one self-contained `MANUAL RELAY PACKET`. Copy the whole packet into a **new
temporary web chat**. Copy only the model's answer back into the terminal, then type `.submit` on a
line by itself.

A multiline JSON answer is accepted. If copying into the terminal is inconvenient, save the answer
to a UTF-8 text file and enter:

```text
.file path/to/answer.txt
```

Enter `.abort` to stop the run deliberately.

## Why every packet uses a fresh chat

The runtime already serializes the permitted system message, recent history, CORE_MEMORY,
WORKING_MEMORY, ARCHIVE_PEEK and current Sensorium frame into each packet. Reusing a web chat would
add hidden provider-side history. It would also allow a probe call to contaminate later agent calls.
A fresh chat keeps every model invocation stateless in the same sense as the API adapters.

## Resume after interruption

Every exchange is written to the configured relay directory:

```text
manual-sessions/deepseek-web/
  000000.request.json
  000000.request.md
  000000.response.txt
  000001.request.json
  ...
```

Restart the same command with the same config. The runtime deterministically replays saved responses
until it reaches the first unanswered packet. Before replaying, it verifies the SHA-256 hash of each
newly generated request. If the protocol, seed, memory stream or prior response changed, replay stops
instead of silently attaching stale answers to a different experiment.

To begin a genuinely new run, change `model.relay_dir` or move the previous directory aside.

## Manual profile design

The supplied web profiles use 18 simulator ticks and a dependency-free hash-ngram semantic control.
They include coupled, disconnected, remapped and working-context interruption segments plus periodic
prediction and agency probes. Expect roughly 26 copy/paste exchanges.

This is deliberately shorter than the automated battery. It is suitable for inspecting behavior,
checking whether a provider follows the interface and collecting candidate phenomena. It must not be
reported as a powered confirmatory consciousness experiment.

## Direct hosted APIs

For unattended exploratory runs, provider configs are also included:

```bash
export DEEPSEEK_API_KEY=...
embodied-llm doctor --config configs/providers/deepseek-api.yaml
embodied-llm run --config configs/providers/deepseek-api.yaml

export GEMINI_API_KEY=...
embodied-llm doctor --config configs/providers/gemini-api.yaml
embodied-llm run --config configs/providers/gemini-api.yaml
```

The DeepSeek profile uses the OpenAI-compatible chat-completions transport with JSON mode. The Gemini
profile uses Google's native `generateContent` request shape and JSON MIME mode. Provider model names
and endpoints are configuration, not assumptions baked into the runtime; update the YAML when a
provider changes its catalogue.

## Interpretation boundary

Manual relay can reveal interesting causal learning, ownership reports, memory use and adaptation.
It cannot establish that different web providers received identical hidden instructions or decoding
conditions. Compare manual runs qualitatively, and reserve quantitative cross-model claims for sealed
API/local-model protocols with explicit versions and sampling controls.
